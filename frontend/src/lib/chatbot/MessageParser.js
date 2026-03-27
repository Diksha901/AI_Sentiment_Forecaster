class MessageParser {
  constructor(actionProvider) {
    this.actionProvider = actionProvider;
  }

  parse(message) {
    const lowerCaseMessage = message.toLowerCase();

    // Route all messages to Groq service for intelligent responses
    // The intent-based routing is now handled by Groq's language understanding

    if (
      lowerCaseMessage.includes('hello') ||
      lowerCaseMessage.includes('hi') ||
      lowerCaseMessage.includes('hey')
    ) {
      this.actionProvider.handleGreeting();
    } else if (
      lowerCaseMessage.includes('account') ||
      lowerCaseMessage.includes('billing') ||
      lowerCaseMessage.includes('subscription')
    ) {
      this.actionProvider.handleAccountQuestion();
    } else if (
      lowerCaseMessage.includes('api') ||
      lowerCaseMessage.includes('integrate') ||
      lowerCaseMessage.includes('connect')
    ) {
      this.actionProvider.handleAPIQuestion();
    } else if (
      lowerCaseMessage.includes('data') ||
      lowerCaseMessage.includes('source') ||
      lowerCaseMessage.includes('upload')
    ) {
      this.actionProvider.handleDataQuestion();
    } else if (
      lowerCaseMessage.includes('report') ||
      lowerCaseMessage.includes('share') ||
      lowerCaseMessage.includes('export')
    ) {
      this.actionProvider.handleReportQuestion();
    } else {
      // All other messages go to Groq for intelligent processing
      this.actionProvider.handleDefault(message);
    }
  }
}

export default MessageParser;
