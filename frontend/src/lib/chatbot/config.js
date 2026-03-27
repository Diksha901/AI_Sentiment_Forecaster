import { createChatBotMessage } from 'react-chatbot-kit';

const config = {
  initialMessages: [createChatBotMessage(`Hi! I'm TrendAI support. How can I help?`)],
  botName: "TrendBot",
  customStyles: {
    botMessageBox: {
      backgroundColor: '#3b82f6', 
    },
    chatButton: {
      backgroundColor: '#3b82f6',
    },
  },
};

export default config;