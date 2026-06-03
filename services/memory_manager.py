class MemoryManager:
    """
    Manages conversational memory using a sliding window strategy.
    Limits memory to the last N turns or a maximum token count.
    """

    def get_context(
        self, chat_history: list, max_turns: int = 3, max_tokens: int = 1500
    ):
        """
        Extracts recent conversation history.
        Returns: (context_string, num_tokens_used, num_turns_used)
        """
        if not chat_history:
            return "", 0, 0

        # Approximation: 1 token ~= 4 characters
        max_chars = max_tokens * 4

        # Group flat chat_history into Question/Answer pairs
        turns = []
        current_user = None
        for msg in chat_history:
            if msg["role"] == "user":
                current_user = msg["content"]
            elif msg["role"] == "assistant" and current_user is not None:
                turns.append((current_user, msg["content"]))
                current_user = None

        if not turns:
            return "", 0, 0

        # Extract the last N turns
        recent_turns = turns[-max_turns:]

        # Build context backwards to prioritize the most recent turns if we hit limits
        context_parts = []
        current_chars = 0

        for user_msg, ast_msg in reversed(recent_turns):
            turn_str = f"User: {user_msg}\nAssistant: {ast_msg}\n\n"
            # If adding this turn exceeds max characters (and we have at least 1 turn), break
            if current_chars + len(turn_str) > max_chars and current_chars > 0:
                break

            context_parts.insert(0, turn_str)
            current_chars += len(turn_str)

        final_context = "".join(context_parts).strip()
        num_turns = len(context_parts)
        num_tokens = current_chars // 4

        return final_context, num_tokens, num_turns
