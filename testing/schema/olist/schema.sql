-- Generated DDL for postgresql
-- Generated at: 2025-08-25T10:15:56.827807

CREATE TABLE "olist_sellers_dataset" (
    "seller_id" VARCHAR(64) NOT NULL,
    "seller_zip_code_prefix" INTEGER NOT NULL,
    "seller_city" VARCHAR(80) NOT NULL,
    "seller_state" VARCHAR(4) NOT NULL,
    PRIMARY KEY ("seller_id")
);

CREATE TABLE "product_category_name_translation" (
    "column_1" VARCHAR(92) NOT NULL,
    "column_2" VARCHAR(78) NOT NULL,
    PRIMARY KEY ("column_1")
);

CREATE TABLE "olist_orders_dataset" (
    "order_id" VARCHAR(64) NOT NULL,
    "customer_id" VARCHAR(64) NOT NULL,
    "order_status" VARCHAR(22) NOT NULL,
    "order_purchase_timestamp" TIMESTAMP NOT NULL,
    "order_approved_at" TIMESTAMP,
    "order_delivered_carrier_date" TIMESTAMP,
    "order_delivered_customer_date" TIMESTAMP,
    "order_estimated_delivery_date" TIMESTAMP NOT NULL,
    PRIMARY KEY ("order_id"),
    FOREIGN KEY ("customer_id") REFERENCES "olist_customers_dataset" ("customer_id")
);

CREATE TABLE "olist_order_items_dataset" (
    "order_id" VARCHAR(64) NOT NULL,
    "order_item_id" INTEGER NOT NULL,
    "product_id" VARCHAR(64) NOT NULL,
    "seller_id" VARCHAR(64) NOT NULL,
    "shipping_limit_date" TIMESTAMP NOT NULL,
    "price" DECIMAL(10,2) NOT NULL,
    "freight_value" DECIMAL(10,2) NOT NULL,
    PRIMARY KEY ("order_id", "order_item_id"),
    FOREIGN KEY ("order_id") REFERENCES "olist_orders_dataset" ("order_id"),
    FOREIGN KEY ("product_id") REFERENCES "olist_products_dataset" ("product_id"),
    FOREIGN KEY ("seller_id") REFERENCES "olist_sellers_dataset" ("seller_id")
);

CREATE TABLE "olist_customers_dataset" (
    "customer_id" VARCHAR(64) NOT NULL,
    "customer_unique_id" VARCHAR(64) NOT NULL,
    "customer_zip_code_prefix" INTEGER NOT NULL,
    "customer_city" VARCHAR(50) NOT NULL,
    "customer_state" VARCHAR(4) NOT NULL,
    PRIMARY KEY ("customer_id")
);

CREATE TABLE "olist_geolocation_dataset" (
    "geolocation_zip_code_prefix" INTEGER NOT NULL,
    "geolocation_lat" DECIMAL(12,4) NOT NULL,
    "geolocation_lng" DECIMAL(12,4) NOT NULL,
    "geolocation_city" VARCHAR(18) NOT NULL,
    "geolocation_state" VARCHAR(4) NOT NULL,
    "id" INTEGER SERIAL NOT NULL,
    PRIMARY KEY ("id")
);

CREATE TABLE "olist_order_payments_dataset" (
    "order_id" VARCHAR(64) NOT NULL,
    "payment_sequential" BOOLEAN NOT NULL,
    "payment_type" VARCHAR(22) NOT NULL,
    "payment_installments" INTEGER NOT NULL,
    "payment_value" DECIMAL(10,2) NOT NULL,
    PRIMARY KEY ("order_id"),
    FOREIGN KEY ("order_id") REFERENCES "olist_orders_dataset" ("order_id")
);

CREATE TABLE "olist_order_reviews_dataset" (
    "review_id" VARCHAR(64) NOT NULL,
    "order_id" VARCHAR(64) NOT NULL,
    "review_score" INTEGER NOT NULL,
    "review_comment_title" VARCHAR(50),
    "review_comment_message" VARCHAR(255),
    "review_creation_date" TIMESTAMP NOT NULL,
    "review_answer_timestamp" TIMESTAMP NOT NULL,
    PRIMARY KEY ("review_id"),
    FOREIGN KEY ("order_id") REFERENCES "olist_orders_dataset" ("order_id")
);

CREATE TABLE "olist_products_dataset" (
    "product_id" VARCHAR(64) NOT NULL,
    "product_category_name" VARCHAR(92),
    "product_name_lenght" INTEGER,
    "product_description_lenght" INTEGER,
    "product_photos_qty" INTEGER,
    "product_weight_g" INTEGER,
    "product_length_cm" INTEGER,
    "product_height_cm" INTEGER,
    "product_width_cm" INTEGER,
    PRIMARY KEY ("product_id"),
    FOREIGN KEY ("product_category_name") REFERENCES "product_category_name_translation" ("column_1")
);
