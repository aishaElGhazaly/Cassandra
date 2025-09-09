# 🎧 Cassandra
*Your personal music editor & curator*

Cassandra transforms music discovery into intimate storytelling. Built with the depth and warmth of Apple Music's editorial descriptions, it weaves cultural context, historical insight, and emotional resonance into every analysis and recommendation.

---

## 🌟 What Makes Cassandra Different

Unlike algorithmic recommendation engines that reduce music to data points, Cassandra approaches music as living art shaped by human experience, culture and historical influence.  

Every response feels like a conversation with a trusted music editor who understands not just what sounds good, but why it matters.

- **Editorial Mode**: Cassandra tells the story of songs, albums, artists, genres, or decades. She explains the cultural forces that shaped the work. Every piece of music exists within a larger narrative that Cassandra illuminates with intimacy and authority.  
- **Recommendation Mode**: When you need new music, Cassandra curates with purpose. She suggests **8 tracks or 3 albums**, each accompanied by commentary that captures essence and significance. Her recommendations aren’t just lists—they’re carefully woven stories that help you understand why these particular works belong together.

---

## 💫 The Experience

Cassandra is ephemeral by design. No signups, no logins, no saved conversations. Each interaction is a fresh encounter with music, encouraging exploration without the weight of digital permanence.  

The interface fades away, leaving only the conversation between you and the music. 

Her prose flows naturally:
- **Concise but never shallow**  
- **Authoritative but never cold**  
- **Paragraphs, not bullet points**  
- **Rhythm and readability above all**  

---

## 🧠 Technical Foundation

- **Current Version**: Deployed on Streamlit with GPT-5 Nano; optimized for cost efficiency while still leveraging a powerful LLM.
- **Memory**: Intelligent conversation summarization ensures context remains coherent across long sessions.  
- **Architecture**:  
  - `logic.py` → LangChain orchestration and prompt management  
  - `app.py` → Streamlit interface and conversation flow    

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit + custom CSS for typography & layout  
- **Backend**: LangChain orchestration with OpenAI GPT-5 Nano
- **Memory**: Context summarizer for long conversations powered by GPT-5 Nano. 
- **Deployment**: Streamlit Cloud (v1) → Hugging Face Spaces (future)  

---

## 🔮 Future Development:  
- **Knowledge enhancement**: Wikipedia retrieval for cultural and historical grounding, and for releases post-cutoff 
- **Real-time data**: Spotify API integration for accurate discographies and new music beyond May 2024
- **Hosting expansion**: Migration to Hugging Face Spaces for improved performance and accessibility

---

*Cassandra represents a return to music discovery as personal journey rather than algorithmic suggestion. It reminds us that every song carries history, every album tells a story, and every recommendation is an invitation to understand music more deeply.*  
