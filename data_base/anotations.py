from pydantic import BaseModel, Field


class GoodBase(BaseModel):
    product_id: int = Field(..., description="ID товара для получения информации о товаре")



class OrderBase(BaseModel):
    user_id: str = Field(..., description="ID пользователя для кого нужно оформить заказ")
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., description="Количество товара")
    is_delivery: bool = Field(..., description="Необходима ли доставка")

