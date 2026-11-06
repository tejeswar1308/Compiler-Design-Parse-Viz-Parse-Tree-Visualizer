"""Pydantic models for grammar API requests."""

from typing import Optional, Any
from pydantic import BaseModel, model_validator


class GrammarInput(BaseModel):
    grammar_text: str = ""
    grammar: Optional[str] = None
    start_symbol: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_grammar_text(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "grammar" in values and not values.get("grammar_text"):
                values["grammar_text"] = values["grammar"]
            elif "grammar_text" in values and not values.get("grammar"):
                values["grammar"] = values["grammar_text"]
        return values


class ParseRequest(BaseModel):
    grammar_text: str = ""
    grammar: Optional[str] = None
    input_string: str = ""
    input: Optional[str] = None
    start_symbol: Optional[str] = None
    use_transformed: bool = False

    @model_validator(mode="before")
    @classmethod
    def populate_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "grammar" in values and not values.get("grammar_text"):
                values["grammar_text"] = values["grammar"]
            elif "grammar_text" in values and not values.get("grammar"):
                values["grammar"] = values["grammar_text"]
            if "input" in values and not values.get("input_string"):
                values["input_string"] = values["input"]
            elif "input_string" in values and not values.get("input"):
                values["input"] = values["input_string"]
        return values


class PracticeCheckRequest(BaseModel):
    question_id: str
    answer: str
    question_data: dict


class TransformRequest(BaseModel):
    grammar_text: str = ""
    grammar: Optional[str] = None
    start_symbol: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_grammar(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "grammar" in values and not values.get("grammar_text"):
                values["grammar_text"] = values["grammar"]
            elif "grammar_text" in values and not values.get("grammar"):
                values["grammar"] = values["grammar_text"]
        return values
