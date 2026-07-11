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
            
            # Academic Policies & Escalations
            ("Minimum attendance for exams?", "Woxsen maintains a high standard for academic participation, so the minimum required attendance is 75%. If you fall below this, you might be barred from writing your end-semester exams."),
            ("What to do for attendance shortage?", "If you have an attendance shortage, contact your course faculty first. If unresolved, contact your Program Manager. Be prepared to provide a medical certificate if applicable."),
            ("How to apply for medical leave?", "To apply for medical leave, contact your Course Faculty first, and then your Program Manager. You must submit a valid medical certificate."),
            ("Academic calendar release?", "The academic calendar is your roadmap for the semester! It's usually published 4–6 weeks before the semester starts on the student portal at portal.woxsen.edu.in."),
            ("How to apply for exam revaluation?", "To apply for revaluation, contact the Controller of Examinations. You must submit a revaluation application and payment receipt. Typical processing time is 2–4 weeks."),
            ("Who to contact for Transfer Certificate?", "To apply for a Transfer Certificate, contact the Registrar Office. You must submit department clearance and a No Due Certificate. The processing time is 5–10 working days."),
            
            # Student Support / Certificates
            ("How to get a bonafide certificate?", "To get a bonafide certificate, contact the Bridge Helpdesk. You only need to provide your Student ID. The processing time is 1–3 working days."),
            ("How to apply for a transcript?", "To get your transcript, contact the Bridge Helpdesk. You must submit an application and complete the payment if applicable. The processing time is 5–10 working days."),
            
            # Hostel & Wi-Fi
            ("Who to contact for hostel room change?", "To request a room change, contact Hostel Support (Gateway) with a written request stating your reason. Room change approvals are subject to room availability."),
            ("Hostel wifi is not working?", "For hostel Wi-Fi issues, contact the IT Help Desk. You will need to provide your hostel room, Student ID, and device information."),
            ("ERP login issue or password reset?", "For ERP login issues or password resets, contact the IT Help Desk with your Roll Number, registered email, and a screenshot of the error."),
            
            # Library
            ("What if library book is missing or damaged?", "If a library book is missing, contact the library staff. They can help with reservation, alternative copy, or a digital copy. If a book is damaged, report it immediately to the library staff; fines depend on the library policy."),
            
            # Transport
            ("Who to contact for transport issues?", "For transport or bus route issues, contact the Transport Office. You will need to provide your bus route and Student ID."),
            
            # Ragging (High Priority)
            ("How to file a ragging complaint?", "If you have a ragging complaint, contact the Anti-Ragging Cell immediately. Ragging complaints are treated as high priority. You can email antiragging.cell@woxsen.edu.in or call emergency numbers 7416664429 or 9709704747."),
            
            # Placements & Internships
            ("Who to contact for internships and placements?", "For internship and placement queries, contact Career Connect at careerconnect@woxsen.edu.in."),
            
            # Scholarships & Fees
            ("Who handles scholarship queries?", "For scholarship queries, contact the Accounts Office. You will need to provide your scholarship documents and income certificate (if required)."),
            ("Paid fees but status not updated?", "If your fee payment is not updated, contact the Accounts Office with your Transaction ID, payment screenshot, date of payment, and amount paid. The typical resolution time is 1–3 working days."),
            
            # General Support
            ("How to apply for student exchange?", "That's exciting! To apply, you'll need at least a 60% average and have completed 1 year (for UG) or 2 trimesters (for PG). Applications open in March and August. You can reach out to international@woxsen.edu.in for more details."),
            ("Lost my ID card?", "If you lost your ID card, contact the Bridge Helpdesk first. You will need to provide your Student ID Number, identity proof, and a passport-size photo (if requested). Processing time is approximately 2–7 working days.")
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
        return {"total_chunks": 5, "sources": [{"id": "doc1", "source": "Mock University Student Handbook 2024"}, {"id": "doc2", "source": "Mock Admin Directory"}]}

    def delete_source(self, source_name: str) -> int:
        return 0