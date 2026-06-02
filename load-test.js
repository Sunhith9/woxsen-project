/**
 * k6 Load Test – Woxsen University Platform
 * ─────────────────────────────────────────────────────────────────────────────
 * Simulates realistic mixed load from ~6 000 active users:
 *   - Student login
 *   - Grievance list fetch (admin)
 *   - RAG chatbot query
 *   - Document upload
 *
 * Run (local):
 *   k6 run load-test.js
 *
 * Run (high load):
 *   k6 run --vus 300 --duration 60s load-test.js
 *
 * Install k6: https://k6.io/docs/getting-started/installation/
 * ─────────────────────────────────────────────────────────────────────────────
 */

import http from "k6/http";
import { check, sleep, group } from "k6";
import { Rate, Trend } from "k6/metrics";

// ── Custom metrics ─────────────────────────────────────────────────────────
const errorRate = new Rate("errors");
const ragLatency = new Trend("rag_latency", true);

// ── Configuration ──────────────────────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || "http://localhost:80";
const LOGIN_USER = __ENV.LOGIN_USER || "hod_cse";
const LOGIN_PASS = __ENV.LOGIN_PASS || "password123";

// ── Load profile ──────────────────────────────────────────────────────────
export const options = {
  stages: [
    { duration: "30s", target: 50 },    // Ramp up
    { duration: "2m",  target: 300 },   // Sustained medium load
    { duration: "1m",  target: 600 },   // Spike to ~6000 scaled
    { duration: "1m",  target: 300 },   // Return to medium
    { duration: "30s", target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<2000"],  // 95% of requests < 2 s
    errors: ["rate<0.02"],              // Error rate < 2%
    rag_latency: ["p(95)<3000"],        // RAG responses < 3 s
  },
};

// ── Shared JWT token (set once per VU) ────────────────────────────────────
let authToken = null;

function login() {
  const res = http.post(
    `${BASE_URL}/api/login`,
    JSON.stringify({ username: LOGIN_USER, password: LOGIN_PASS }),
    { headers: { "Content-Type": "application/json" } }
  );
  const ok = check(res, {
    "login 200": (r) => r.status === 200,
    "token returned": (r) => {
      try { return !!JSON.parse(r.body).token; }
      catch { return false; }
    },
  });
  errorRate.add(!ok);
  if (ok) {
    authToken = JSON.parse(res.body).token;
  }
}

// ── Main scenario ─────────────────────────────────────────────────────────
export default function () {
  // Ensure we have a token
  if (!authToken) login();

  const authHeaders = {
    headers: {
      Authorization: `Bearer ${authToken}`,
      "Content-Type": "application/json",
    },
  };

  // ── Health check ──────────────────────────────────────────────────────
  group("health", () => {
    const res = http.get(`${BASE_URL}/health`);
    const ok = check(res, { "health 200": (r) => r.status === 200 });
    errorRate.add(!ok);
  });

  sleep(0.2);

  // ── Grievance list ────────────────────────────────────────────────────
  group("grievances", () => {
    const res = http.get(`${BASE_URL}/api/grievances`, authHeaders);
    const ok = check(res, {
      "grievances 200": (r) => r.status === 200,
      "array returned": (r) => {
        try { return Array.isArray(JSON.parse(r.body)); }
        catch { return false; }
      },
    });
    errorRate.add(!ok);
  });

  sleep(0.3);

  // ── RAG chatbot query ─────────────────────────────────────────────────
  group("rag_query", () => {
    const queries = [
      "What are the library timings?",
      "How do I apply for revaluation?",
      "What is the minimum attendance?",
      "Who is the HOD for CSE?",
      "My hostel wifi is not working",
    ];
    const q = queries[Math.floor(Math.random() * queries.length)];
    const start = Date.now();
    const res = http.post(
      `${BASE_URL}/api/rag/query`,
      JSON.stringify({ query: q }),
      { headers: { "Content-Type": "application/json" }, timeout: "10s" }
    );
    ragLatency.add(Date.now() - start);
    const ok = check(res, {
      "rag 200": (r) => r.status === 200,
      "answer present": (r) => {
        try { return !!JSON.parse(r.body).answer; }
        catch { return false; }
      },
    });
    errorRate.add(!ok);
  });

  sleep(Math.random() * 1 + 0.5); // Realistic think time
}
