// Groq Chat Service for real-time responses
import { apiFetch } from './api';

// Fallback knowledge base for common questions
const KNOWLEDGE_BASE = {
  'how it works': 'TrendAI uses advanced AI and machine learning to analyze market trends and consumer sentiment. Our platform processes data through our RAG (Retrieval Augmented Generation) pipeline, which combines ChromaDB vector storage with Groq LLM to deliver intelligent insights. Simply connect your data sources, and our system automatically enriches and analyzes the information to provide actionable market intelligence.',
  'data connection': 'To connect your data source: 1) Go to Settings > Data Connections, 2) Click "Add Source", 3) Choose from AWS S3, Google BigQuery, Snowflake, or upload CSV files directly. Our system supports real-time and batch data ingestion.',
  'api integration': 'Our REST API allows seamless integration with your applications. You can query market trends, sentiment analysis, and custom reports programmatically. Access our API documentation in the Help Center for endpoints and authentication details.',
  'pricing': 'We offer three plans: Free (10 AI queries/month, 5GB storage), Pro Business (80 queries/month, 60GB storage) at ₹10,000, and Enterprise (100 queries/month, 100GB storage) at ₹20,000. Choose the plan that fits your needs!',
  'support': 'Our support team is available 24/7. You can reach us through our chat, email at support@trendai.com, or the Help Center. We typically respond within 5 minutes.',
};

export const groqChatService = {
  async getResponse(userMessage) {
    try {
      console.log('[INFO] Sending message to Groq:', userMessage);

      // Call backend endpoint that interfaces with Groq
      const res = await apiFetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage })
      });

      console.log('[INFO] Response status:', res.status);

      if (res.ok) {
        const data = await res.json();
        console.log('[INFO] Groq response:', data);

        // Try different response field names for compatibility
        const response = data.response || data.answer || data.result;
        if (response) {
          return response;
        }
      } else {
        const errorData = await res.json();
        console.error('[ERROR] RAG API Error:', res.status, errorData);
      }

      // Fallback: Try to match with knowledge base
      return this.getFallbackResponse(userMessage);
    } catch (error) {
      console.error('[ERROR] Groq chat error:', error);
      return this.getFallbackResponse(userMessage);
    }
  },

  getFallbackResponse(userMessage) {
    const message = userMessage.toLowerCase();

    // Check for keyword matches in knowledge base
    for (const [key, answer] of Object.entries(KNOWLEDGE_BASE)) {
      if (message.includes(key)) {
        return answer;
      }
    }

    // Default response for unknown queries
    return "I'm here to help! You can ask me about: \n• How TrendAI works\n• Connecting data sources\n• API integration\n• Pricing plans\n• Support options\n\nWhat would you like to know more about?";
  }
};
