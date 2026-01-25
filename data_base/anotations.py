from pydantic import BaseModel, Field
from typing import Annotated, Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(BaseModel):
    user_id: str
    messages: Annotated[Sequence[BaseMessage], add_messages]


class CategoryBase(BaseModel):
    category_id: int = Field(..., description="ID категории, для которой нужно получить список товаров")


class CategoryCityBase(BaseModel):
    category_id: int = Field(..., description="ID категории, для которой нужно получить список товаров")
    city_id: int

class GoodBase(BaseModel):
    product_id: int = Field(..., description="ID товара для получения информации о товаре")


class CartBase(BaseModel):
    user_id: str = Field(..., description="ID пользователя корзины")
    product_id: int = Field(..., description="ID товара в корзине")
    quantity: int = Field(..., description="Количество товара в корзине")
    is_delivery: bool = Field(..., description="Необходима ли доставка товара")


class CartAddBase(BaseModel):
    user_id: str = Field(..., description="ID пользователя корзины")
    product_id: int = Field(..., description="ID товара в корзине")
    quantity: int = Field(..., description="Количество товара в корзине")
    total_price: int = Field(..., description="Общая сумма покупки товара в корзине")


class OrderBase(BaseModel):
    user_id: str = Field(..., description="ID пользователя для кого нужно оформить заказ")

# class ArendaGoodBase(BaseModel):
#     good_id: int = Field(..., description="ID арендного товара для получения информации об аренде товара")



    # state: AgentState = Field(..., description="сотоянеие пользователя из которго получаем user_id=state.user_id")
    # total_price: int = Field(..., description="Общая сумма покупки товара в корзине")


# class ArendaCartBase(BaseModel):
#     user_id: str = Field(..., description="ID пользователя корзины аренды")
#     good_id: int = Field(..., description="ID товара в корзине")
#     quantity: int = Field(..., description="Количество товара в корзине")
#     arenda_time: int = Field(..., description="Время аренды")
#     is_contract: bool = Field(..., description="Хочет ли клиент заключить договор")


# class ArendaCartAddBase(BaseModel):
#     user_id: str = Field(..., description="ID пользователя корзины аренды")
#     good_id: int = Field(..., description="ID товара в корзине")
#     quantity: int = Field(..., description="Количество товара в корзине")
#     arenda_time: int = Field(..., description="Время аренды")
#     total_price: int = Field(..., description="Общая сумма покупки товара в корзине")

    # stage: str = "intro"  # ["intro", "company", "categories", "goods", "good_detail", "order"]
    # messages: list = Field(default_factory=list)
