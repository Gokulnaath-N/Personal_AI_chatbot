import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
import logging
from typing import Optional, Dict, Any, List

class GraniteHF:
    def __init__(self, model_id: str, hf_token: str, device: str = None):
        """
        Initialize the IBM Granite model with the given model ID and Hugging Face token.
        
        Args:
            model_id: The model ID from Hugging Face (e.g., 'ibm-granite/granite-3.3-2b-instruct')
            hf_token: Hugging Face authentication token
            device: Device to run the model on ('cuda', 'mps', or 'cpu'). Auto-detects if None.
        """
        self.model_id = model_id
        self.hf_token = hf_token
        
        # Set device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        else:
            self.device = device
            
        # Initialize model and tokenizer
        self.model = None
        self.tokenizer = None
        
        # Set seed for reproducibility
        self.seed = 42
        set_seed(self.seed)
        
        self._load_model()
    
    def _load_model(self):
        """Load the model and tokenizer."""
        try:
            # Load model with the specified configuration
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map=self.device,
                torch_dtype=torch.bfloat16 if 'cuda' in self.device else torch.float32,
                token=self.hf_token
            )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                token=self.hf_token
            )
            
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
            raise
    
    def chat(self, system_prompt: str, user_message: str, **generation_kwargs) -> str:
        """
        Generate a response using the IBM Granite model.
        
        Args:
            system_prompt: System prompt/instruction
            user_message: User's message
            **generation_kwargs: Additional arguments for text generation
                (e.g., max_new_tokens, temperature, top_p, etc.)
                
        Returns:
            Generated response as a string
        """
        try:
            # Format the conversation
            conv = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Apply chat template with the same parameters as in the example
            input_ids = self.tokenizer.apply_chat_template(
                conv,
                return_tensors="pt",
                thinking=True,
                return_dict=True,
                add_generation_prompt=True
            ).to(self.device)
            
            # Set default generation parameters if not provided
            generation_params = {
                'max_new_tokens': generation_kwargs.get('max_new_tokens', 1024),
                'temperature': generation_kwargs.get('temperature', 0.7),
                'top_p': generation_kwargs.get('top_p', 0.9),
                'do_sample': generation_kwargs.get('do_sample', True),
                'repetition_penalty': generation_kwargs.get('repetition_penalty', 1.1),
                'eos_token_id': self.tokenizer.eos_token_id,
                'pad_token_id': self.tokenizer.pad_token_id or self.tokenizer.eos_token_id
            }
            
            # Set seed for reproducibility
            set_seed(self.seed)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **input_ids,
                    **{k: v for k, v in generation_params.items() if k not in ['thinking', 'return_dict', 'add_generation_prompt']}
                )
            
            # Decode the response
            response = self.tokenizer.decode(
                outputs[0][input_ids["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in chat generation: {error_msg}")
            return f"I apologize, but I encountered an error: {error_msg}. Please try again later."
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'model') and self.model is not None:
            del self.model
        if hasattr(self, 'tokenizer') and self.tokenizer is not None:
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()