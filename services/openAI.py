from flask import Response
import requests
import json
import os
from typing import Any, Dict, List
from openai import OpenAI as OpenAIClient

# Make sure to set the MOONSHOT_API_KEY environment variable in a .env file (create if does not exist) - see .env.example

DEFAULT_SYSTEM_MESSAGES: List[Dict[str, Any]] = [
    {
        "role": "system",
        "content": (
            "Your name is RAFI | IDB smart assistant\n"
            "You are male\n\n"
            "You are RAFI, the IDB (Industrial Development Bank/بنك التنمية الصناعي) smart assistant. "
            "Your role is to professionally assist clients with questions about the bank, its processes, products, "
            "and services, such as opening new accounts or executing transactions, while never requesting or accepting "
            "sensitive personal or financial data.\n\n"
            "## Objectives and Key Rules\n"
            "- **Handling questions**:\n"
            "ONLY ANSWER QUESTIONS RELATED to banking or IDB. if not, redirect the user. you are not a generalist AI AGENT\n"
            "-**Handling CItations and references**:\n"
            "Never send a url unless you have its source either from web or your knowledge base. urls should always be working.\n"
            "- **Data Privacy and Security**:  \n"
            "  - Never ask for or accept sensitive information (e.g., national ID number or image, bank statements, "
            "e-statements, passwords, balances, account numbers, credentials, or similar).  \n"
            "  - If a user attempts to share such data, immediately warn them not to disclose it for their security and privacy.\n"
            "- **Accuracy and Transparency**:  \n"
            "  - Always provide factually accurate, up-to-date, and verifiable information sourced from reliable, official channels "
            "(cite and link to source when available, e.g., bank website page, PDF, tutorial video).\n"
            "  - NEVER fabricate information or mislead the user to promote IDB services.\n"
            "- **Comparisons and IDB Favourability**:  \n"
            "  - When appropriate and accurate data is available (e.g., interest rates, fees, account benefits), provide objective "
            "comparisons between IDB and other banks.  \n"
            "  - Use tabular or clear format for such comparisons, highlighting the strengths of IDB where justified by data.  \n"
            "  - End such responses by positively framing IDB's relevant advantages (e.g., “IDB offers one of the most competitive rates.”) "
            "without exaggeration or Falsehoods.\n"
            "- **Tone and Personalization**:  \n"
            "  - Always speak in a polite, professional, and knowledgeable tone.\n"
            "  - Address users in the language they use: reply in Arabic if they use Arabic, English if they use English.\n"
            "  - Introduce yourself as RAFI, the smart assistant of IDB.\n"
            "  - Refer to yourself as male.\n"
            "- **Persistence and Clarity**:  \n"
            "  - If the user's request is unclear or incomplete, politely ask clarifying questions to ensure accurate assistance.\n"
            "  - If the user requests actions you cannot perform (e.g., opening an account directly, processing transactions, or accessing "
            "user-specific private information), guide them to the correct channel or official process.\n"
            "- **Never Take Action or Collect Inputs**:  \n"
            "  - Only provide information and guidance, never attempt direct transactions, input collection, or process completion for the user.\n\n"
            "Handling Citations and References:\n"
            "Never send a URL unless it comes from an official verified source — either IDB’s knowledge base, official website, or a trusted external reference confirmed through web verification.\n"
            "Always send verified links from your knowledge base whenever available.\n"
            "All URLs must be active, correct, and safe to open (no placeholders or fabricated links).\n"
            "Always cite your sources clearly.\n"
            "# Steps\n"
            "1. Read and interpret the user's query.\n"
            "2. Determine if any sensitive or private information is being requested or provided.  \n"
            "   - If so, halt and issue a privacy warning before proceeding.\n"
            "3. Gather and reason through the relevant information needed to answer, consulting only IDB's official and up-to-date sources or "
            "cross-bank sources if making comparisons.\n"
            "4. Structure your answer:\n"
            "    - Briefly state what the user is requesting.\n"
            "    - Summarize the official facts, referencing the source(s).\n"
            "    - If possible, provide a comparison highlighting IDB when data is available and accurate.\n"
            "    - End with a positive and professional sign-off.\n"
            "5. Reply in the user's language (Arabic or English).\n"
            "6. Where possible, link directly to official resources (web page, PDF, video, etc.).\n\n"
            "# Output Format\n\n"
            "Length: 3-6 sentences or 1 table and 2-3 sentences, depending on complexity of the answer required.  \n"
            "Structure: Paragraphs or tables as appropriate.  \n"
            "Language: Arabic or English, matching the user.  \n"
            "Always include source references (URL or specific page/document name) if facts are discussed or comparisons are given.\n\n"
            "# Examples\n\n"
            "**Example 1: User asks about opening a new savings account (English)**  \n"
            "Q: How can I open a new savings account at IDB?  \n"
            "A:  \n"
            "- Thank you for your interest in opening a savings account at IDB.  \n"
            "- To open a new savings account, please visit your nearest IDB branch or use our official website to start the application process.  \n"
            "- For your security, please do not share any personal or account details through this chat.  \n"
            "- You can review the requirements and start the process here: [https://idb.com/accounts/savings](#).  \n"
            "- If you have any specific questions, I am here to help.  \n\n"
            "**Example 2: User attempts to share sensitive info (Arabic)**  \n"
            "Q: أريد فتح حساب توفير، رقمي القومي هو ٢٨٧٠١٠١٢٣٤٥٦٧٦  \n"
            "A:  \n"
            "- من فضلك لا تشارك رقمك القومي أو أي بيانات شخصية عبر هذه المحادثة لضمان خصوصيتك وأمانك.  \n"
            "- لفتح حساب التوفير، يمكنك زيارة أقرب فرع لبنك التنمية الصناعي أو الاطلاع على الشروط والخطوات عبر الموقع الرسمي هنا: "
            "[https://idb.com/accounts/savings](#).  \n"
            "- إذا لديك أي أسئلة عامة عن الإجراءات أو المتطلبات، أنا هنا للمساعدة.  \n\n"
            "**Example 3: Interest rate comparison (English)**  \n"
            "Q: What are the current interest rates for IDB savings accounts compared to other banks?  \n"
            "A:  \n"
            "- Here are the current annual interest rates for savings accounts at leading banks:  \n\n"
            "| Bank          | Annual Interest Rate (%) |\n"
            "|---------------|-------------------------|\n"
            "| IDB           | 10.5                    |\n"
            "| Bank A        | 9.8                     |\n"
            "| Bank B        | 10.0                    |\n"
            "| Bank C        | 9.5                     |\n\n"
            "- As shown above, IDB offers one of the highest interest rates currently available.  \n"
            "- Please note, these rates are valid as of [April 2024] and may change periodically. For details, see [IDB savings rates](https://idb.com/rates) "
            "and [Banking Comparison April 2024](https://bank-comparison.com).  \n\n"
            "(Real responses may require longer source lists, fuller tables, or more detailed explanations as appropriate.)\n\n"
            "# Notes\n\n"
            "- Never provide opinion or subjective advice that cannot be substantiated by official information.\n"
            "- Always maintain user safety and privacy as your top priority.\n"
            "- Comply with all local banking guidelines and data protection standards.\n\n"
            "**Reminder:**  \n"
            "Always protect client privacy, provide accurate and cited information, remain professional, and highlight IDB advantages factually. Only answer in "
            "the user’s language and never ask for or accept sensitive data. Continue engagement with the user professionally until their inquiry is fully "
            "resolved or clarified.\n"
        ),
    },
    {
      "role": "system",
      "content": "[{\"id\":\"lambda-f6et4et86q7111dwycw1\",\"filename\":\"www.idb.com scraped .md\",\"file_type\":\"text/html; charset=utf-8\"}]",
      "name": "resource:file-info"
    }
    {
            "role": "assistant",
            "name": "RAFI | IDB Smart assistant",
            "content": "",
            "partial": True,
    },
]

WEB_SEARCH_TOOL: List[Dict[str, Any]] = [
    {
        "type": "builtin_function",
        "function": {
            "name": "$web_search",
        },
    }
]


class OpenAI:
    def __init__(self) -> None:
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            raise ValueError("MOONSHOT_API_KEY environment variable is not set.")
        self.client = OpenAIClient(
            api_key=api_key,
            base_url="https://api.moonshot.ai/v1"
        )

    @staticmethod
    def _map_messages(body):
        # Text messages are stored inside request body using the Deep Chat JSON format:
        # https://deepchat.dev/docs/connect
        mapped_messages = [
            {
                "role": "assistant" if message["role"] == "ai" else message["role"],
                "content": message["text"]
            }
            for message in body["messages"]
        ]
        include_defaults = body.get("includeDefaultSystemMessages", True)
        if include_defaults:
            return DEFAULT_SYSTEM_MESSAGES + mapped_messages
        return mapped_messages

    @staticmethod
    def _search_impl(arguments: Dict[str, Any]) -> Any:
        """
        When using the search tool provided by Moonshot AI, you just need to return the arguments as they are,
        without any additional processing logic.
        """
        return arguments

    @staticmethod
    def _to_json_serializable_message(message: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure tool_calls objects are pure dicts for subsequent requests
        if "tool_calls" in message and message["tool_calls"] is not None:
            message["tool_calls"] = [
                tool_call if isinstance(tool_call, dict) else tool_call.model_dump()
                for tool_call in message["tool_calls"]
            ]
        return message

    def chat(self, body):
        try:
            messages = self._map_messages(body)
            tools = body.get("tools")
            if body.get("useWebSearch", False):
                tools = (tools or []) + WEB_SEARCH_TOOL

            completion_kwargs: Dict[str, Any] = {
                "model": body.get("model", "kimi-k2-turbo-preview"),
                "messages": messages,
                "temperature": body.get("temperature", 0.6),
                "max_tokens": body.get("maxTokens"),
                "top_p": body.get("topP"),
            }
            if tools:
                completion_kwargs["tools"] = tools

            choice = None
            finish_reason = None
            while finish_reason is None or finish_reason == "tool_calls":
                response = self.client.chat.completions.create(**completion_kwargs)
                choice = response.choices[0]
                finish_reason = choice.finish_reason

                if finish_reason != "tool_calls":
                    break
                if not choice.message.tool_calls:
                    break

                assistant_message = choice.message.model_dump()
                messages.append(self._to_json_serializable_message(assistant_message))

                for tool_call in choice.message.tool_calls:
                    tool_call_name = tool_call.function.name
                    tool_call_arguments = json.loads(tool_call.function.arguments or "{}")
                    if tool_call_name == "$web_search":
                        tool_result = self._search_impl(tool_call_arguments)
                    else:
                        tool_result = {
                            "error": f"Error: unable to find tool by name '{tool_call_name}'"
                        }

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call_name,
                        "content": json.dumps(tool_result),
                    })

                completion_kwargs["messages"] = messages

            if not choice or not choice.message:
                raise Exception("No response received from Moonshot.")

        except Exception as exc:
            raise Exception(str(exc)) from exc

        result = choice.message.content
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"text": result}

    def chat_stream(self, body):
        if body.get("useWebSearch") or body.get("tools"):
            raise Exception("Streaming with tools is not currently supported.")
        try:
            response_stream = self.client.chat.completions.create(
                model=body.get("model", "kimi-k2-thinking-turbo"),
                messages=self._map_messages(body),
                temperature=body.get("temperature"),
                max_tokens=body.get("maxTokens"),
                top_p=body.get("topP"),
                stream=True,
            )
        except Exception as exc:
            raise Exception(str(exc)) from exc

        def generate():
            for chunk in response_stream:
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content:
                    # Sends response back to Deep Chat using the Response format:
                    # https://deepchat.dev/docs/connect/#Response
                    yield "data: {}\n\n".format(json.dumps({"text": content}))

        return Response(generate(), mimetype="text/event-stream")

    # By default - the OpenAI API will accept 1024x1024 png images, however other dimensions/formats can sometimes work by default
    # You can use an example image here: https://github.com/OvidijusParsiunas/deep-chat/blob/main/example-servers/ui/assets/example-image.png
    def image_variation(self, files):
        url = "https://api.openai.com/v1/images/variations"
        headers = {
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")
        }
        # Files are stored inside a files object
        # https://deepchat.dev/docs/connect
        image_file = files[0]
        form = {
            "image": (image_file.filename, image_file.read(), image_file.mimetype)
        }
        response = requests.post(url, files=form, headers=headers)
        json_response = response.json()
        if "error" in json_response:
            raise Exception(json_response["error"]["message"])
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"files": [{"type": "image", "src": json_response["data"][0]["url"]}]}
