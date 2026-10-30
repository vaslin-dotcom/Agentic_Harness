from langchain_core.messages import AIMessage,ToolMessage

RECENT=3
MIN_ARG=200
HARD_LIMIT=20000

def truncate_middle(text: str, limit: int = 6000) -> str:
    if len(text) <= limit:
        return text
    half = limit // 2
    cut = len(text) - limit
    return (
        text[:half]
        + f"\n... [{cut} chars cut from the middle; rerun with a narrower command, "
        + "e.g. pipe through head, tail or grep] ...\n"
        + text[-half:]
    )

def tool_call_index(messages):
    index={}
    for m in messages:
        if isinstance(m, AIMessage):
            for tool_call in m.tool_calls:
                index[tool_call['id']] = (tool_call['name'],tool_call['args'])
    return index

def short(args, limit=40):
    text = str(args)
    return text if len(text) <= limit else text[:limit] + "..."

def shrink_args(args):
    new = {}
    for key, value in args.items():
        if isinstance(value, str) and len(value) > MIN_ARG:
            new[key] = (f"[{len(value)} chars omitted from an old call. "
                        f"Do not copy this text. Read the file from disk if you need it.]")
        else:
            new[key] = value
    return new

def build_view(messages):
    calls = tool_call_index(messages)
    tool_positions=[i for i,m in enumerate(messages) if isinstance(m,ToolMessage)]
    old_messages=set(tool_positions[:-RECENT])
    cutoff = tool_positions[-RECENT] if len(tool_positions) > RECENT else 0

    view=[]
    for i,m in enumerate(messages):
        if i in old_messages:
            name,args=calls.get(m.tool_call_id)
            note=f"""
                 The old results are cleared to save context, it came from {name},{short(args)}, you can run it again if needed
                 """
            if len(note) < len(str(m.content)):
                view.append(ToolMessage(content=note, tool_call_id=m.tool_call_id))
                continue

            if isinstance(m, AIMessage) and m.tool_calls and i < cutoff:
                new_calls = [{**c, "args": shrink_args(c["args"])} for c in m.tool_calls]
                view.append(m.model_copy(update={"tool_calls": new_calls}))
                continue

            if isinstance(m, ToolMessage) and len(str(m.content)) > HARD_LIMIT:
                view.append(ToolMessage(
                    content=truncate_middle(str(m.content), HARD_LIMIT),
                    tool_call_id=m.tool_call_id,
                ))
                continue
        else:
            view.append(m)
    return view
