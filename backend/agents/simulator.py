import asyncio
import os
import json
from typing import AsyncGenerator
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from agents.tools import get_agent_tools

load_dotenv()

async def simulate_autonomous_loop(
    query: str, 
    mode: str = "chat",
    model_name: str = "gemini-2.5-flash",
    project_dir: str = None
) -> AsyncGenerator[str, None]:
    
    if not project_dir:
        # Default workspace if none provided
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "workspace"))

    def emit(event_type: str, agent: str, message: str, meta: dict = None):
        payload = {
            "type": event_type,
            "agent": agent,
            "message": message,
            "meta": meta or {}
        }
        return f"data: {json.dumps(payload)}\n\n"

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        yield emit("error", "System", "GOOGLE_API_KEY is missing. Cannot use agentic tools.", {})
        return

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
        
        if mode == "builder":
            tools = get_agent_tools(project_dir)
            llm = llm.bind_tools(tools)
            system_prompt = (
                f"You are an elite Autonomous AI Builder. Your working directory is: {project_dir}\n"
                "You have tools to write files, run terminal commands, read existing files, and edit files.\n"
                "If the user asks you to build a project, write the necessary files and run commands (e.g. npm init, pip install).\n"
                "If the user asks you to modify or resolve code, use `read_file` to see the current code, and `edit_file` to replace specific blocks of code, or `write_file` to rewrite it entirely.\n"
                "Think step-by-step. Do NOT write all files at once if you need to run commands to initialize a project first.\n"
                "When you are finished with the task, explain what you did and stop calling tools.\n"
                "CRITICAL: Always provide the final run command to start the project, and a list of any libraries the user needs to install at the very end of your final response."
            )
        else:
            system_prompt = "You are a helpful, brilliant AI Copilot. Answer the user's queries concisely and accurately."
            
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        max_iterations = 15
        
        for iteration in range(max_iterations):
            yield emit("thought", "System Agent", f"Thinking... (Iteration {iteration+1})", {"model": model_name})
            
            final_message = None
            async for chunk in llm.astream(messages):
                if chunk.content:
                    yield emit("action", "AI Copilot", chunk.content, {"model": model_name})
                if final_message is None:
                    final_message = chunk
                else:
                    final_message += chunk
            
            messages.append(final_message)
            
            if not final_message.tool_calls:
                # No tools called, the AI is done!
                yield emit("complete", "EIN Copilot", "Task complete.", {})
                break
                
            # The AI wants to call tools!
            for tool_call in final_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                # Format args for display
                args_display = json.dumps(tool_args, indent=2)
                yield emit("thought", "System Agent", f"🛠️ Calling Tool: **{tool_name}**\n```json\n{args_display}\n```", {"model": model_name})
                
                # Execute tool
                tool_instance = next((t for t in tools if t.name == tool_name), None)
                if tool_instance:
                    try:
                        # Langchain tools can be invoked synchronously
                        result = tool_instance.invoke(tool_args)
                    except Exception as e:
                        result = f"Tool execution failed: {str(e)}"
                else:
                    result = f"Unknown tool: {tool_name}"
                    
                yield emit("thought", "System Agent", f"✅ Tool Output:\n```text\n{result}\n```", {"model": model_name})
                
                # Append tool result to messages so the LLM can read it
                messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))
                
        else:
            yield emit("error", "System Agent", "Max iterations reached. Stopping to prevent infinite loops.", {})

    except Exception as e:
        yield emit("error", "System", f"Agent loop failed: {str(e)}", {})
