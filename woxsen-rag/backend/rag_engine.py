"""
rag_engine.py
=============
Layer 2: Mock Full RAG pipeline for testing frontend flow without ChromaDB/C++ Build Tools.

Usage:
    engine = RAGEngine()
    result = await engine.query("What are the library timings?")
"""

import logging
import os

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Mock RAG pipeline for Woxsen University support.
    Bypasses vector database for easy testing on Windows machines
    missing C++ build tools.
    """

    def __init__(self):
        # FAQ knowledge base — always available regardless of ML deps
        self.faqs = [
            # Identity & Capabilities
            ("Who are you and what can you do?", "I am the Woxsen AI Support Assistant! I'm here to help you navigate campus life, answer your university-related questions, and help you resolve grievances. I can provide information on ID cards, hostel issues, library rules, marks correction, and much more. Think of me as your 24/7 digital guide to Woxsen!"),
            ("How can you help me?", "I can help you in many ways! If you have an issue with your ID card, fees, or hostel room, just let me know. I can also guide you through the process of revaluation, faculty concerns, and student exchange programs. My goal is to give you instant solutions so you don't have to wait for an admin response."),
            ("What is your name?", "You can call me the Woxsen Support Bot! I'm your dedicated AI companion designed to make your student life easier by providing quick answers and support."),
            
            # SOT & SOB
            ("Who is the Dean of SOT?", "The Dean of the School of Technology (SOT) is Pep Lluis Esteva de Rosa. He leads our technology programs and is committed to academic excellence."),
            ("Who is the HOD for CSE and AIML?", "The Head of Department for CSE and AIML is Dr. Anand Kakarla. He oversees the academic and research initiatives for these departments."),
            ("Who is the MBA HOD at SOB?", "Dr. K. Hemachandran is a senior faculty member at the School of Business (SOB). For the current HOD designation, it's best to contact the SOB office directly at sob@woxsen.edu.in or call 040-6810-0100."),
            ("Where are the CSE labs?", "The CSE labs are conveniently located in the Lab Block, where you'll find all the necessary equipment and resources for your practical work."),
            
            # Campus Facilities
            ("Where is the Student Wellness Center?", "You can find the Student Wellness Center in the Academic Block. It's there to support your physical and mental well-being."),
            ("What are the library timings?", "Our library has great hours! It's open from 9:00 AM to 2:00 AM daily. On weekends, you can visit from 10:00 AM to 5:00 PM."),
            ("What are the cafeteria timings?", "We have several options for you! The main mess timings are: Breakfast (7–10 AM), Lunch (12–3 PM), and Dinner (7–10 PM). Also, there are 4 cafés on campus that stay open until 1 AM for late-night snacks!"),
            
            # Academic Policies
            ("Minimum attendance for exams?", "Woxsen maintains a high standard for academic participation, so the minimum required attendance is 75%. If you fall below this, you might be barred from writing your end-semester exams."),
            ("Makeup exam if sick?", "I'm sorry to hear you're unwell! If you miss an exam due to illness, you should submit a written application to your HOD within 3 days. Make sure to include a medical certificate. Once the HOD approves it, they'll forward it to the Exam Cell in Room 105."),
            ("Academic calendar release?", "The academic calendar is your roadmap for the semester! It's usually published 4–6 weeks before the semester starts on the student portal at portal.woxsen.edu.in."),
            ("Marks are wrong or affected?", "I understand how frustrating that is! You can apply for revaluation within 7 days of your result declaration. Head over to the Exam Cell in Room 105. There's a fee of ₹500 per subject, and you'll typically get the results in about 21 working days."),
            
            # Grievances & Support
            ("Hostel wifi is not working?", "I know how important Wi-Fi is! Start by reporting it to the Hostel Warden in Block H. If it's an urgent technical issue, you can visit the IT Help Desk at the Library Ground Floor or send an email to it@woxsen.edu.in."),
            ("No electricity in hostel room?", "That's an inconvenience, I'm sorry! Please raise a Maintenance Request under 'Hostel → Electrical Issue' in the portal. If it's an emergency, select 'Urgent'. A technician should be there within 24 hours. If they don't show up, please inform your warden."),
            ("Can I withdraw a grievance?", "Yes, you can! Just send an email to grievance@woxsen.edu.in or visit Room 301. Just keep in mind that you can only withdraw it as long as a final decision hasn't been issued yet."),
            ("Someone is misbehaving or harassment?", "I am very sorry you're dealing with this. Woxsen takes these matters very seriously and you can report it confidentially under 'Harassment / Misconduct' in the portal. A committee will contact you privately within 3 days. For urgent help, please visit the Support Desk at the Gateway immediately."),
            ("Complaint against faculty?", "If you have a concern or complaint regarding a faculty member, please visit the Admin Office at the Gateway or email grievance@woxsen.edu.in. Your feedback is important and will be handled professionally."),
            ("Grievance not resolved in 24 hours?", "For critical cases like ragging, we escalate immediately to the Dean of Student Affairs (Room 301). For other issues, our standard response times are: Critical (2 days), High (5 days), and Medium (7 days)."),
            
            # Fees
            ("Paid fees but status not updated?", "Don't worry, these things take a little time to process. Please upload your receipt in the support form under 'Fees Payment Not Updated'. The Finance team will verify it within 24-48 hours. If it's been longer than that, visit the Gachibowli Office with your proof of payment."),
            
            # General Help
            ("How to apply for student exchange?", "That's exciting! To apply, you'll need at least a 60% average and have completed 1 year (for UG) or 2 trimesters (for PG). Applications open in March and August. You can reach out to international@woxsen.edu.in for more details."),
            ("Lost my ID card?", "Oh no! First, double-check your room and the places you've visited. If you still can't find it, raise a 'Lost ID Request' via Gateway → Student Support → Bridge. There's a ₹200 replacement fee, and your new card will be ready in 3-5 days.")
        ]

        # Try to load semantic search model (optional — falls back to keyword matching)
        self.model = None
        self.faq_embeddings = None
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.faq_embeddings = self.model.encode([q for q, a in self.faqs])
        except Exception as e:
            logger.error(f"Sentence transformers unavailable: {e}. Using keyword fallback.")

        # Conversation history {conversation_id: [{"role": ..., "parts": ...}]}
        self.conversations = {}

    async def query(self, question: str, conversation_id: str = None) -> dict:
        """
        Mock RAG pipeline for a student question, using semantic embedding search.
        Now includes a greeting detector and more helpful fallbacks.
        """
        logger.info(f"Mocking NLP RAG response for query: {question}")
        answer = None
        q_lower = question.lower().strip()
        
        # Simple Greeting Detector
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings"]
        if any(g in q_lower for g in greetings) and len(q_lower.split()) <= 3:
            answer = "Hello there! I'm the Woxsen AI Support Assistant. How can I help you today? You can ask me about hostel issues, ID cards, or even academic rules!"
        
        base_answer = None
        
        if not answer and self.model:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                import numpy as np
                q_emb = self.model.encode([question])
                sims = cosine_similarity(q_emb, self.faq_embeddings)[0]
                best_idx = np.argmax(sims)
                best_score = sims[best_idx]
                
                if best_score > 0.45:
                    base_answer = self.faqs[best_idx][1]
            except Exception as e:
                logger.error(f"Error during semantic search: {e}")
                
        # Keyword Fallback 
        if not answer and not base_answer:
            for q, a in self.faqs:
                words = q.lower().replace("?", "").replace(",", "").split()
                significant_words = [w for w in words if len(w) > 3 and w not in ["what", "when", "where", "who", "how", "this", "that"]]
                if any(sw in q_lower.split() for sw in significant_words) and len(significant_words) > 0:
                    base_answer = a
                    break
        
        # Generate the final conversational response with Gemini via REST API (bypassing outdated local SDK)
        try:
            import requests
            api_key = os.getenv("GEMINI_API_KEY", "")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set in environment")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            # Use base_answer as the strict rule/context
            context_str = f"Relevant Woxsen Fact/Policy:\n{base_answer}" if base_answer else "General conversation. No specific Woxsen policy applies."
            
            # Initialize conversation history if it doesn't exist
            if conversation_id and conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
                
            history = self.conversations.get(conversation_id, [])

            # System prompt for Gemini
            prompt = f"""You are the 'Woxsen AI Support Assistant', a helpful and highly intelligent digital guide for Woxsen University students.

CRITICAL INSTRUCTIONS:
1. NEVER introduce yourself (e.g., "Hello there! I'm...") unless the user's message is ONLY a greeting like "hi", "who are you", or "what can you do". 
2. If the user asks a question or states a problem, dive STRAIGHT into the answer. Do not say "I am the support assistant...".
3. Write completely naturally like a human. Avoid repetitive robotic phrases.
4. If a 'Relevant Woxsen Fact/Policy' is provided below, base your answer heavily on it.
5. If the context says 'General conversation. No specific Woxsen policy applies.' and the user is complaining or asking about an unknown issue, DO NOT say "I don't have those details." Instead, briefly acknowledge their issue, apologize for the inconvenience, and advise them to "complain to the respective department and wait, it will be resolved soon" as requested by the admin. 

{context_str}"""

            # Build multi-turn payload
            contents = []
            
            # 1. System Instruction as first user message (if model doesn't support systemInstruction block natively without errors)
            # It's cleaner to put the system prompt in the first user message for standard flash API.
            
            # 2. Append history
            # To ensure it parses correctly, alternate user and model.
            for turn in history:
                contents.append(turn)
            
            # 3. Append current question
            # If no history, prepend the system prompt to the user's first question
            if not history:
                contents.append({
                    "role": "user",
                    "parts": [{"text": f"{prompt}\n\nStudent: {question}"}]
                })
            else:
                contents.append({
                    "role": "user",
                    "parts": [{"text": question}]
                })

            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 800
                }
            }
            
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            
            res_data = response.json()
            answer = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Update history
            if conversation_id:
                # Store the user message
                if not history:
                    self.conversations[conversation_id].append({
                        "role": "user",
                        "parts": [{"text": f"{prompt}\n\nStudent: {question}"}]
                    })
                else:
                    self.conversations[conversation_id].append({
                        "role": "user",
                        "parts": [{"text": question}]
                    })
                # Store the model message
                self.conversations[conversation_id].append({
                    "role": "model",
                    "parts": [{"text": answer}]
                })
                # Trim history to last 10 messages (5 turns)
                if len(self.conversations[conversation_id]) > 10:
                    self.conversations[conversation_id] = self.conversations[conversation_id][-10:]

            logger.info("Successfully generated conversational response from Gemini REST API.")
        except Exception as e:
            logger.error(f"Gemini REST API failed: {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                logger.error(f"Gemini API Response Body: {response.text}")
            
            # Ultimate Fallback if API fails
            if base_answer:
                if "Woxsen AI Support Assistant" not in base_answer and "Woxsen Support Bot" not in base_answer:
                    import random
                    intros = ["Based on the Woxsen guidelines, ", "Let me check that for you... Ah yes, ", "I can certainly help with that. "]
                    answer = f"{random.choice(intros)}{base_answer}"
                else:
                    answer = base_answer
            else:
                answer = ("I'm sorry, I don't have the specific details on that just yet, but I'm learning more about Woxsen every day! "
                          "Could you try rephrasing your question? Or, if it's urgent, you can always contact the Admin Office at admin@woxsen.edu.in or call 040-6810-0100.")



        return {
            "type": "rag",
            "answer": answer,
            "sources": ["Woxsen Semantic AI DB", "Woxsen Admin Directory"],
            "doc_count": 10,
            "chunks_used": 1
        }

    def ingest_documents(self, docs: list) -> int:
        return 0

    def get_stats(self) -> dict:
        return {"total_chunks": 5, "sources": ["Mock University Student Handbook 2024", "Mock Admin Directory"]}

    def delete_source(self, source_name: str) -> int:
        return 0