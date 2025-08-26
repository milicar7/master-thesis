-- Generated DDL for postgresql
-- Generated at: 2025-08-26T20:40:40.916699

CREATE TABLE "olist_sellers_dataset" (
    "seller_id" VARCHAR(255) NOT NULL,
    "seller_zip_code_prefix" INTEGER NOT NULL,
    "seller_city" VARCHAR(255) NOT NULL,
    "seller_state" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("seller_id")
);

CREATE TABLE "product_category_name_translation" (
    "product_category_name" VARCHAR(255) NOT NULL,
    "product_category_name_english" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("product_category_name")
);

CREATE TABLE "olist_orders_dataset" (
    "order_id" VARCHAR(255) NOT NULL,
    "customer_id" VARCHAR(255) NOT NULL,
    "order_status" VARCHAR(255) NOT NULL,
    "order_purchase_timestamp" TIMESTAMP NOT NULL,
    "order_approved_at" TIMESTAMP,
    "order_delivered_carrier_date" TIMESTAMP,
    "order_delivered_customer_date" TIMESTAMP,
    "order_estimated_delivery_date" TIMESTAMP NOT NULL,
    PRIMARY KEY ("order_id"),
    FOREIGN KEY ("customer_id") REFERENCES "olist_customers_dataset" ("customer_id")
);

-- NORMALIZATION SUGGESTIONS:
-- [3NF] olist_orders_dataset: Transitive dependency detected: order_delivered_carrier_date, order_delivered_customer_date, order_approved_at, order_status, order_estimated_delivery_date, order_purchase_timestamp depends on customer_id, creating transitive dependency through primary key. Consider extracting to a separate 'customer_id_details' columns_and_types with columns: customer_id, order_delivered_carrier_date, order_delivered_customer_date, order_approved_at, order_status, order_estimated_delivery_date, order_purchase_timestamp.
--   Confidence: 1.0

CREATE TABLE "olist_order_items_dataset" (
    "order_id" VARCHAR(255) NOT NULL,
    "order_item_id" INTEGER NOT NULL,
    "product_id" VARCHAR(255) NOT NULL,
    "seller_id" VARCHAR(255) NOT NULL,
    "shipping_limit_date" TIMESTAMP NOT NULL,
    "price" DECIMAL(18,6) NOT NULL,
    "freight_value" DECIMAL(18,6) NOT NULL,
    PRIMARY KEY ("order_id", "order_item_id"),
    FOREIGN KEY ("order_id") REFERENCES "olist_orders_dataset" ("order_id"),
    FOREIGN KEY ("product_id") REFERENCES "olist_products_dataset" ("product_id"),
    FOREIGN KEY ("seller_id") REFERENCES "olist_sellers_dataset" ("seller_id")
);

-- NORMALIZATION SUGGESTIONS:
-- [2NF] olist_order_items_dataset: Column 'product_id' has partial dependency on 'order_id' (part of composite key ['order_id', 'order_item_id']) instead of depending on the full key (strength: 96.7%). Consider extracting to a separate 'order_product_id' table with columns: order_id, product_id.
--   Confidence: 1.0

-- [2NF] olist_order_items_dataset: Column 'seller_id' has partial dependency on 'order_id' (part of composite key ['order_id', 'order_item_id']) instead of depending on the full key (strength: 98.7%). Consider extracting to a separate 'order_seller_id' table with columns: order_id, seller_id.
--   Confidence: 1.0

-- [2NF] olist_order_items_dataset: Column 'shipping_limit_date' has partial dependency on 'order_id' (part of composite key ['order_id', 'order_item_id']) instead of depending on the full key (strength: 99.7%). Consider extracting to a separate 'order_shipping_limit_date' table with columns: order_id, shipping_limit_date.
--   Confidence: 1.0

-- [2NF] olist_order_items_dataset: Column 'price' has partial dependency on 'order_id' (part of composite key ['order_id', 'order_item_id']) instead of depending on the full key (strength: 97.6%). Consider extracting to a separate 'order_price' table with columns: order_id, price.
--   Confidence: 1.0

-- [2NF] olist_order_items_dataset: Column 'freight_value' has partial dependency on 'order_id' (part of composite key ['order_id', 'order_item_id']) instead of depending on the full key (strength: 97.9%). Consider extracting to a separate 'order_freight_value' table with columns: order_id, freight_value.
--   Confidence: 1.0

CREATE TABLE "olist_customers_dataset" (
    "customer_id" VARCHAR(255) NOT NULL,
    "customer_unique_id" VARCHAR(255) NOT NULL,
    "customer_zip_code_prefix" INTEGER NOT NULL,
    "customer_city" VARCHAR(255) NOT NULL,
    "customer_state" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("customer_id")
);

-- NORMALIZATION SUGGESTIONS:
-- [3NF] olist_customers_dataset: Transitive dependency detected: customer_state depends on customer_zip_code_prefix, creating transitive dependency through primary key. Consider extracting to a separate 'customer_zip_code_prefix_details' columns_and_types with columns: customer_zip_code_prefix, customer_state.
--   Confidence: 0.9

CREATE TABLE "olist_geolocation_dataset" (
    "geolocation_zip_code_prefix" INTEGER NOT NULL,
    "geolocation_lat" DECIMAL(18,6) NOT NULL,
    "geolocation_lng" DECIMAL(18,6) NOT NULL,
    "geolocation_city" VARCHAR(255) NOT NULL,
    "geolocation_state" VARCHAR(255) NOT NULL,
    "id" INTEGER SERIAL NOT NULL,
    PRIMARY KEY ("id")
);

CREATE TABLE "olist_order_payments_dataset" (
    "order_id" VARCHAR(255) NOT NULL,
    "payment_sequential" BOOLEAN NOT NULL,
    "payment_type" VARCHAR(255) NOT NULL,
    "payment_installments" INTEGER NOT NULL,
    "payment_value" DECIMAL(18,6) NOT NULL,
    PRIMARY KEY ("order_id"),
    FOREIGN KEY ("order_id") REFERENCES "olist_orders_dataset" ("order_id")
);

CREATE TABLE "olist_order_reviews_dataset" (
    "review_id" VARCHAR(255) NOT NULL,
    "order_id" VARCHAR(255) NOT NULL,
    "review_score" INTEGER NOT NULL,
    "review_comment_title" VARCHAR(255),
    "review_comment_message" VARCHAR(255),
    "review_creation_date" TIMESTAMP NOT NULL,
    "review_answer_timestamp" TIMESTAMP NOT NULL,
    PRIMARY KEY ("review_id"),
    FOREIGN KEY ("order_id") REFERENCES "olist_orders_dataset" ("order_id")
);

-- NORMALIZATION SUGGESTIONS:
-- [1NF] olist_order_reviews_dataset: Column 'review_comment_message' contains multi-valued data in 38.8% of rows. Consider splitting into separate columns or creating a separate 'review_comment_message_values' table.
--   Confidence: 0.4

CREATE TABLE "olist_products_dataset" (
    "product_id" VARCHAR(255) NOT NULL,
    "product_category_name" VARCHAR(255),
    "product_name_lenght" INTEGER,
    "product_description_lenght" INTEGER,
    "product_photos_qty" INTEGER,
    "product_weight_g" INTEGER,
    "product_length_cm" INTEGER,
    "product_height_cm" INTEGER,
    "product_width_cm" INTEGER,
    PRIMARY KEY ("product_id"),
    FOREIGN KEY ("product_category_name") REFERENCES "product_category_name_translation" ("product_category_name")
);
