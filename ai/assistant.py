"""AI Assistant with OpenAI Function Calling"""
import json
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from loguru import logger

import config
from ai.prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_MALE, SYSTEM_PROMPT_FEMALE, TOOLS
from ai.product_search import (
    search_products,
    get_company_info,
    format_products_list
)


class AIAssistant:
    """AI Assistant for EWA PRODUCT"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        # Если нужен прокси для OpenAI, раскомментируй:
        # import httpx
        # http_client = httpx.AsyncClient(proxies="http://proxy_address:port")
        # self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY, http_client=http_client)
        
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
        logger.info(f"AI Assistant initialized with model: {self.model}")
    
    async def get_response(
        self,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        assistant_gender: Optional[str] = None
    ) -> tuple[str, List[Dict], str]:
        """
        Get AI response for user message.
        
        Args:
            user_message: User's message text
            chat_history: Previous chat history (list of {"role": "...", "content": "..."})
            assistant_gender: 'male', 'female', or None
            
        Returns:
            Tuple of (response_text, found_products, search_query)
        """
        # Variables to store found products
        found_products = []
        search_query = ""
        
        try:
            # Select system prompt based on gender
            if assistant_gender == "male":
                system_prompt = SYSTEM_PROMPT_MALE
            elif assistant_gender == "female":
                system_prompt = SYSTEM_PROMPT_FEMALE
            else:
                system_prompt = SYSTEM_PROMPT
            
            # Build messages list
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add chat history
            if chat_history:
                messages.extend(chat_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"Sending request to OpenAI: {user_message[:100]}...")
            
            # First API call - check if functions needed
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # Check if function calls needed
            if response_message.tool_calls:
                # Add assistant response with tool calls to messages
                messages.append(response_message)
                
                # Context to store products from function calls
                context = {"found_products": [], "search_query": ""}
                
                # Process each function call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Function call: {function_name} with args {function_args}")
                    
                    # Execute function
                    function_response = await self._execute_function(
                        function_name,
                        function_args,
                        context
                    )
                    
                    # Add function response to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response
                    })
                
                # Store found products and query
                found_products = context["found_products"]
                search_query = context["search_query"]
                
                # Second API call with function results
                second_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                
                final_answer = second_response.choices[0].message.content
            else:
                # No function calls needed - direct answer
                final_answer = response_message.content
            
            logger.info(f"AI response generated: {len(final_answer)} characters")
            return final_answer, found_products, search_query
            
        except Exception as e:
            logger.error(f"Error in AI assistant: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте еще раз.", [], ""
    
    async def _execute_function(self, function_name: str, arguments: Dict, context: Dict) -> str:
        """
        Execute function call.
        
        Args:
            function_name: Name of function to execute
            arguments: Function arguments
            context: Dictionary to store products and query for this request
            
        Returns:
            Function result as JSON string
        """
        try:
            if function_name == "search_products":
                query = arguments.get("query", "")
                # Игнорируем max_results от GPT, всегда ищем больше для пагинации
                max_results = 20
                
                products = search_products(query, max_results)
                
                # Store ALL found products and query in context (for this request only)
                context["found_products"] = products if products else []
                context["search_query"] = query
                
                if products:
                    # Format only TOP-3 products for GPT (pagination handled by buttons)
                    top_3 = products[:3]
                    formatted = format_products_list(top_3)
                    result = {
                        "status": "success",
                        "count": len(products),  # Total count
                        "shown": len(top_3),     # Shown to user
                        "products": formatted
                    }
                else:
                    result = {
                        "status": "not_found",
                        "message": f"Продукты по запросу '{query}' не найдены."
                    }
                
                return json.dumps(result, ensure_ascii=False)
            
            elif function_name == "get_company_info":
                info_type = arguments.get("info_type", "all")
                city = arguments.get("city")
                
                info = get_company_info(info_type, city)
                
                if info:
                    result = {
                        "status": "success",
                        "data": info
                    }
                else:
                    result = {
                        "status": "not_found",
                        "message": "Информация не найдена."
                    }
                
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            else:
                return json.dumps({
                    "status": "error",
                    "message": f"Unknown function: {function_name}"
                }, ensure_ascii=False)
        
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            return json.dumps({
                "status": "error",
                "message": str(e)
            }, ensure_ascii=False)

