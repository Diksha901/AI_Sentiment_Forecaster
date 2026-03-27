import { createChatBotMessage } from 'react-chatbot-kit';
import { groqChatService } from '../groq-chat-service';

class ActionProvider {
  constructor(createChatBotMessage, setStateFunc) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
  }

  handleGreeting = () => {
    const message = this.createChatBotMessage(
      "Welcome to TrendAI! 👋 I'm your AI Assistant powered by advanced language models. I can help you with questions about our platform, data analysis, reports, and more. What would you like to know?"
    );
    this.setChatbotMessage(message);
  };

  // Handle any user message with Groq API
  handleUserMessage = async (userMessage) => {
    try {
      // Show loading indicator
      const loadingMessage = this.createChatBotMessage(
        "Analyzing your question...",
        { delay: 0 }
      );
      this.setChatbotMessage(loadingMessage);

      // Get response from Groq API via backend
      const response = await groqChatService.getResponse(userMessage);

      // Remove loading message and add actual response
      this.setState((state) => {
        const messagesWithoutLoading = state.messages.slice(0, -1);
        return {
          ...state,
          messages: [
            ...messagesWithoutLoading,
            this.createChatBotMessage(response, { delay: 500 })
          ]
        };
      });
    } catch (error) {
      console.error('[ERROR] Failed to get response:', error);
      const errorMessage = this.createChatBotMessage(
        "Sorry, I encountered an error processing your request. Please try again."
      );
      this.setChatbotMessage(errorMessage);
    }
  };

  handleAccountQuestion = () => {
    this.handleUserMessage("Tell me about account management and billing options");
  };

  handleAPIQuestion = () => {
    this.handleUserMessage("What are your API capabilities and integration options?");
  };

  handleDataQuestion = () => {
    this.handleUserMessage("How do I connect and manage data sources?");
  };

  handleReportQuestion = () => {
    this.handleUserMessage("How can I create and share reports?");
  };

  handleDefault = async (userMessage) => {
    await this.handleUserMessage(userMessage);
  };

  setChatbotMessage = (message) => {
    this.setState((state) => ({
      ...state,
      messages: [...state.messages, message],
    }));
  };
}

export default ActionProvider;
