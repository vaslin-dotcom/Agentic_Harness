from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage
from agent.context import build_system_prompt
from agent.llm import call_llm, LLMError
from tools.tool_registry import tool_map


def preview(text, limit=500):
    text = str(text)
    return text if len(text) <= limit else text[:limit] + f"... [{len(text) - limit} more chars]"


def loop(messages, max_step=10):
    for step in range(1, max_step + 1):
        try:
            ai_message, usage = call_llm(messages)
        except LLMError as e:
            print(f"[LLM ERROR] {e}")
            return "error"
        messages.append(ai_message)

        print(f"\n--- Step {step} | tokens: {usage.get('total_tokens')} ---")
        if ai_message.content:
            print("AI_MESSAGE :", ai_message.content)

        if not ai_message.tool_calls:
            return "done"

        for tool_call in ai_message.tool_calls:
            print(f"[TOOL CALL] {tool_call['name']}({tool_call['args']})")
            try:
                result = tool_map[tool_call['name']].invoke(tool_call['args'])
            except Exception as e:
                result = f'Error : {e}'
            print(f"[TOOL RESULT] {preview(result)}")
            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call['id'])
            )

    return "max_steps"


if __name__ == "__main__":
    messages = [SystemMessage(content=build_system_prompt())]

    while True:
        human_message = input('HUMAN : ')
        if human_message.strip().lower() == 'exit':
            break
        messages.append(HumanMessage(content=human_message))
        reason = loop(messages)

        if reason == "done":
            print("--- done ---\n")
        elif reason == "max_steps":
            print("Step limit reached. Say 'continue' to let the agent keep going.")
        elif reason == "error":
            print("The model call failed. Send your message again to retry.")