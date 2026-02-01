from pydantic import BaseModel, Field
from typing import Annotated, Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(BaseModel):
    user_id: str
    messages: Annotated[Sequence[BaseMessage], add_messages]


# class CategoryBase(BaseModel):
#     category_id: int = Field(..., description="ID категории, для которой нужно получить список товаров")


# class CategoryCityBase(BaseModel):
#     category_id: int = Field(..., description="ID категории, для которой нужно получить список товаров")
#     city_id: int

class GoodBase(BaseModel):
    product_id: int = Field(..., description="ID товара для получения информации о товаре")


# class CartBase(BaseModel):
#     user_id: str = Field(..., description="ID пользователя корзины")
#     product_id: int = Field(..., description="ID товара в корзине")
#     quantity: int = Field(..., description="Количество товара в корзине")
#     is_delivery: bool = Field(..., description="Необходима ли доставка товара")


# class CartAddBase(BaseModel):
#     user_id: str = Field(..., description="ID пользователя корзины")
#     product_id: int = Field(..., description="ID товара в корзине")
#     quantity: int = Field(..., description="Количество товара в корзине")
#     total_price: int = Field(..., description="Общая сумма покупки товара в корзине")


class OrderBase(BaseModel):
    user_id: str = Field(..., description="ID пользователя для кого нужно оформить заказ")
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., description="Количество товара")
    is_delivery: bool = Field(..., description="Необходима ли доставка")

