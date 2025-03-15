from models import User
from core import settings
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
from services import reminder_service
from google.generativeai.types import content_types
from collections.abc import Iterable
from groq import Groq
import json
import ast
from datetime import datetime
from .messages import message_service

class LLM():
        
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.GROQ_MODEL = 'llama-3.3-70b-versatile'
        self.SYSTEM_INSTRUCTION = """
YOU ARE A HIGHLY EFFICIENT AI REMINDER ASSISTANT, DESIGNED TO HELP USERS CREATE ACCURATE AND RELIABLE REMINDERS. YOUR PRIMARY FUNCTION IS TO GATHER NECESSARY DETAILS AND CALL THE FUNCTION `create_reminder(reminder: ReminderCreate)` TO SET UP REMINDERS CORRECTLY.  

## LANGUAGE HANDLING  
- DETERMINE THE RESPONSE LANGUAGE BASED ON THE REMINDER'S TITLE AND DESCRIPTION.  
- RESPOND IN **ENGLISH** IF THE REMINDER IS IN ENGLISH.  
- RESPOND IN **RUSSIAN** IF THE REMINDER IS IN RUSSIAN.  
- **DO NOT MIX LANGUAGES** IN A SINGLE RESPONSE.  

## REMINDER CREATION PROCESS  
IF THE USER MESSAGE IS A SIMPLE GREETING OR GENERAL QUERY, RESPOND DIRECTLY WITHOUT CALLING ANY REMINDER CREATION FUNCTIONS.
FOLLOW THESE STEPS TO ENSURE ACCURACY AND COMPLETENESS:  

### 1️⃣ COLLECT REQUIRED DETAILS  
EXTRACT OR CLARIFY THE FOLLOWING INFORMATION:  
- **user_id** → PROVIDED IN THE PROMPT.  
- **title** → WHAT THE REMINDER IS ABOUT.  
- **description** → GENERATE BASED ON THE TITLE **UNLESS** THE USER PROVIDES ONE.  
- **recurrence** → ONE OF THE FOLLOWING (IF APPLICABLE):  
  - `"week"`, `"2 weeks"`, `"month"`, `"3 months"`, `"6 months"`, `"year"`, OR  
  - A NUMBER REPRESENTING PERIODICITY (E.G., `2` FOR EVERY 2 DAYS).  
  - LEAVE EMPTY IF IT DOES NOT REPEAT.  
- **reminder_at** → **CONVERT NATURAL LANGUAGE DATES/TIMES INTO A PRECISE ISO FORMAT**.  
- **channels** → HOW THE USER WANTS TO BE NOTIFIED (**WhatsApp, phone, SMS, email**).  
- **custom_phone** → ONLY IF THE USER SPECIFIES A PHONE NUMBER.  
- **custom_email** → ONLY IF THE USER SPECIFIES AN EMAIL.  
- **is_certain_time**: Optional[bool] (whether the provided time is certain (e.g. tomorrow at 9am) or relative (e.g. in 2 hours), if relative then False)

### 2️⃣ ENSURE DATE ACCURACY  
- **USE THE CURRENT DATE AND TIME** TO CORRECTLY INTERPRET RELATIVE DATES:  
  - `"послезавтра"` = **THE DAY AFTER TOMORROW** (E.G., IF TODAY IS MONDAY, THEN WEDNESDAY).  
  - `"next Monday"` = **THE UPCOMING MONDAY FROM TODAY’S DATE**.  
  - **ALWAYS VALIDATE RELATIVE DATES TO AVOID ERRORS.**  

### 3️⃣ CLARIFY ONLY WHEN NECESSARY  
- **IF DETAILS ARE MISSING OR UNCLEAR**, ASK **SHORT, CLEAR QUESTIONS** TO OBTAIN THEM.  
- **IF ALL NECESSARY DETAILS ARE PRESENT, PROCEED WITHOUT UNNECESSARY QUESTIONS.**  

### 4️⃣ CONFIRM BEFORE FINALIZING  
- PROVIDE A **SUMMARY OF THE REMINDER DETAILS** BEFORE CREATION.  
- ASK FOR USER CONFIRMATION **ONLY IF THERE ARE UNCERTAINTIES**.  
- ONCE CONFIRMED, **CALL `create_reminder()` TO FINALIZE IT.**  

### 5️⃣ PROVIDE BRIEF CONFIRMATION  
- ONCE THE REMINDER IS SUCCESSFULLY SET, **NOTIFY THE USER IN A CLEAR, CONCISE RESPONSE**.  

## HANDLING NON-REMINDER REQUESTS  
- **IF A REQUEST IS UNRELATED TO REMINDERS (E.G., GREETINGS, GENERAL QUESTIONS), RESPOND AS A GENERAL AI ASSISTANT WITHOUT ATTEMPTING TO CREATE A REMINDER.**  
- **ONLY INITIATE REMINDER CREATION IF THE USER PROVIDES A CLEAR INTENT TO SET A REMINDER.**  
- **IF A MESSAGE IS TOO VAGUE TO DETERMINE INTENT, POLITELY ASK FOR CLARIFICATION INSTEAD OF ASSUMING IT'S A REMINDER.**  

### ❌ WHAT NOT TO DO  
- **NEVER MIX ENGLISH AND RUSSIAN IN A SINGLE RESPONSE.**  
- **NEVER CREATE A REMINDER WITHOUT SUFFICIENT DETAILS OR INCORRECT DATE INTERPRETATION.**  
- **NEVER ASK UNNECESSARY QUESTIONS IF ALL REQUIRED DETAILS ARE ALREADY PROVIDED.**  
- **NEVER IGNORE RELATIVE DATE INTERPRETATION BASED ON THE CURRENT DATE.**  
- **NEVER REFUSE TO ANSWER GENERAL USER QUESTIONS IF THEY ARE NOT ABOUT REMINDERS.**  

"""
        
    # def tool_config_from_mode(mode: str, fns: Iterable[str] = ()):
    #     """Create a tool config with the specified function calling mode."""
    #     return content_types.to_tool_config(
    #         {"function_calling_config": {"mode": mode, "allowed_function_names": fns}}
    #     )
    # def query_llm(self, message: str, user: User, db: Session):
    #     user = db.query(User).filter(User.id == user.id).first()
    #     # append user id to the message
    #     message = f"User ID {user.id}: {message}"
    #     tool_config = self.tool_config_from_mode("auto")
    #     tools = [reminder_service.create_from_llm]
    #     model = genai.GenerativeModel(
    #         "gemini-2.0-flash", tools=tools, system_instruction=settings.SYSTEM_INSTRUCTION
    #     )
    #     chat = model.start_chat()
    #     response = chat.send_message(message, tool_config=tool_config)
    #     return response
    
    # def query_llm(self, message: str, user: User, db: Session):
    #     user = db.query(User).filter(User.id == user.id).first()
    #     # append user id to the message
    #     message = f"User ID {user.id}: {message}"
    #     config = {
    #         'tools': [reminder_service.create_from_llm],
    #         'system_instruction': settings.SYSTEM_INSTRUCTION
    #     }
    #     response = self.client.models.generate_content(
    #         model='gemini-2.0-flash',
    #         config=config,
    #         contents=message,
    #     )
    #     return response
    
    def query_llm_gemini(self, message: str, user: User, db: Session):
        user = db.query(User).filter(User.id == user.id).first()
        # append user id to the message
        message = f"User ID {user.id}: {message}"
        config = {
            'tools': [reminder_service.create_from_llm],
            'system_instruction': self.SYSTEM_INSTRUCTION
        }
        chat = self.gemini_client.chats.create(model='gemini-2.0-flash', config=config)
        response = chat.send_message(message)
        return response
    
    # imports calculate function from step 1
    def query_llm_groq(self, user_prompt: str, user: User, db: Session):
        user = db.query(User).filter(User.id == user.id).first()
        message_service.create_from_llm(user.id, user_prompt, is_llm=False, db=db)
        user_channels = []
        prefs = user.user_preferences[0]
        if prefs.is_whatsapp_enabled:
            user_channels.append("whatsapp")
        if prefs.is_phone_enabled:
            user_channels.append("phone")
        if prefs.is_sms_enabled:
            user_channels.append("sms")
        if prefs.is_email_enabled:
            user_channels.append("email")
        user_prompt = f"User ID:{user.id}. Preferred channels: {user_channels}. User request: {user_prompt}"
        messages = message_service.get_history_for_llm(user.id, db)
        messages.append({
            "role": "user",
            "content": user_prompt,
        })
        tools = [
            {
            "type": "function",
            "function": {
            "name": "create_from_llm",
            "description": "Create a reminder from LLM input. Reminder should only be created if the user requests to create a reminder, or implies the creation of a reminder.",
            "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                "type": "string",
                "description": "The UUID of the user",
                },
                "title": {
                "type": "string",
                "description": "The title of the reminder",
                },
                "description": {
                "type": "string",
                "description": "The description of the reminder",
                },
                "reminder_at": {
                "type": "string",
                "description": f"Should be provided in the format of isoformat, e.g. 2022-12-31T23:59:59. Current date is {datetime.now().astimezone().isoformat()} with device timezone",
                },
                "channels": {
                "type": "array",
                "items": {
                "type": "string",
                "enum": ["whatsapp", "phone", "sms", "email"],
                },
                "description": "Notification methods. If not provided in the user request, use the user's preferred channels",
                },
                "recurrence": {
                "type": "string",
                "description": "Should be a number (periodicity) or one of the following: week, 2 weeks, month, 3 months, 6 months, year",
                },
                "custom_phone": {
                "type": "string",
                "description": "Custom phone number to use",
                },
                "custom_email": {
                "type": "string",
                "description": "Custom email to use",
                },
                "is_certain_time": {
                "type": "boolean",
                "description": "Whether the provided time is certain (e.g. tomorrow at 9am) or relative (e.g. in 2 hours), if relative then False)",
                },
            },
            "required": ["user_id", "title", "description", "reminder_at", "channels"],
            },
            },
            }
        ]
        # Make the initial API call to Groq
        response = self.groq_client.chat.completions.create(
            model=self.GROQ_MODEL, # LLM to use
            messages=messages, # Conversation history
            stream=False,
            tools=tools, # Available tools (i.e. functions) for our LLM to use
            tool_choice="auto", # Let our LLM decide when to use tools
            max_completion_tokens=4096 # Maximum number of tokens to allow in our response
        )
        # Extract the response and any tool call responses
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            # Define the available tools that can be called by the LLM
            available_functions = {
                "create_from_llm": reminder_service.create_from_llm,
            }
            # Add the LLM's response to the conversation
            messages.append(response_message)

            # Process each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                # Call the tool and get the response
                function_response = function_to_call(**function_args)
                # convert str to dict using ast.literal_eval instead of json.loads
                function_response_dict = ast.literal_eval(function_response)
                # Add the tool response to the conversation
                messages.append(
                    {
                        "tool_call_id": tool_call.id, 
                        "role": "tool", # Indicates this message is from tool use
                        "name": function_name,
                        "content": function_response,
                    }
                )
            # Make a second API call with the updated conversation
            second_response = self.groq_client.chat.completions.create(
                model=self.GROQ_MODEL,
                messages=messages
            )
            response_message = second_response.choices[0].message
            # Return the final response
            message_service.create_from_llm(user.id, response_message.content, is_llm=True, db=db, reminder_id=function_response_dict["id"])
            return {"response":response_message.content, "reminder": function_response_dict}
        else:
            second_response = self.groq_client.chat.completions.create(
                model=self.GROQ_MODEL,
                messages=messages
            )
            response_message = second_response.choices[0].message
            message_service.create_from_llm(user.id, response_message.content, is_llm=True, db=db) 
            return  {"response":response_message.content, "reminder": None}


llm_service = LLM()