from openai import OpenAI
from app.config import get_settings
from typing import List, Dict, Optional, AsyncIterator
import asyncio

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

class ChatKitService:
    def __init__(self):
        self.model = settings.openai_model
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def build_prompt(
        self,
        question: str,
        chunks: List[Dict],
        selection_only: bool = False,
        system_prompt: Optional[str] = None
    ) -> List[Dict]:
        """Build messages for ChatKit"""
        if not system_prompt:
            system_prompt = """You are an embedded RAG chatbot for a published book.
- Answer strictly from the book content; include citations (chapter/section/page/URI).
- If selection-only mode is on, use only the provided selection; otherwise respond "insufficient evidence from the selection."
- Never use external knowledge or speculate; refuse when evidence is weak.
- Be concise, factual, and cite sources inline."""
        
        context = "\n\n".join([
            f"[Source {i+1}] Chapter: {c.get('chapter', 'N/A')}, Section: {c.get('section', 'N/A')}, Page: {c.get('page', 'N/A')}\n{c['text']}"
            for i, c in enumerate(chunks)
        ])
        
        mode_note = " (SELECTION-ONLY MODE: answer only from the provided sources)" if selection_only else ""
        
        user_message = f"""Question: {question}{mode_note}

Retrieved Context:
{context}

Please answer the question based strictly on the context above. Include citations in your response."""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    
    async def stream_answer(
        self,
        question: str,
        chunks: List[Dict],
        selection_only: bool = False
    ) -> AsyncIterator[str]:
        """Stream answer using ChatKit"""
        messages = self.build_prompt(question, chunks, selection_only)
        
        try:
            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.3
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error generating response: {str(e)}"

chatkit_service = ChatKitService()
