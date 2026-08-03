import pytest
from apps.core.daraz.mapping.items import derive_order_status
from apps.core.daraz.mapping.orders import map_order_and_customer
from apps.core.daraz.mapping.products import map_product

@pytest.mark.django_db
class TestMappingAndPrecedence:
    def test_derive_order_status_mixed(self):
        # Precedence: Return > Failed > Shipping > To Ship > Unpaid > Delivered > Cancellation
        
        assert derive_order_status(["Delivered", "Cancellation"]) == "Delivered"
        assert derive_order_status(["Shipping", "Return / Refund", "Delivered"]) == "Return / Refund"
        assert derive_order_status(["Unpaid", "Cancellation"]) == "Unpaid"
        assert derive_order_status(["To Ship", "Shipping"]) == "Shipping"
        
    def test_map_order_and_customer(self):
        payload = {
            "order_id": 12345,
            "customer_first_name": "John",
            "customer_last_name": "Doe",
            "address_shipping": {
                "phone": "03001234567",
                "address1": "123 Main St",
                "city": "Lahore"
            }
        }
        
        o_kwargs, c_kwargs = map_order_and_customer(payload, store_id=1)
        assert o_kwargs["daraz_order_id"] == "12345"
        assert c_kwargs["name"] == "John Doe"
        assert c_kwargs["phone"] == "03001234567"
        assert "hashed_identifier" in c_kwargs

    def test_map_product(self):
        payload = {
            "item_id": 999,
            "attributes": {"name": "Test Item", "brand": "Generic"},
            "skus": [
                {"SkuId": 111, "seller_sku": "SKU-1", "price": "100.00"},
                {"SkuId": 222, "seller_sku": "SKU-2", "price": "150.00"}
            ]
        }
        
        p_kwargs, skus_kwargs = map_product(payload, store_id=1)
        assert p_kwargs["daraz_item_id"] == "999"
        assert p_kwargs["name"] == "Test Item"
        assert len(skus_kwargs) == 2
        assert skus_kwargs[0]["seller_sku"] == "SKU-1"
        assert skus_kwargs[1]["price"] == 150.0
