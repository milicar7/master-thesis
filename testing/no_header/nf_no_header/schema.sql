-- Generated DDL for postgresql
-- Generated at: 2025-09-06T18:10:39.335597

CREATE TABLE "test_nf_data_no_header" (
    "column_1" INTEGER NOT NULL,
    "column_2" VARCHAR(255) NOT NULL,
    "column_3" VARCHAR(255) NOT NULL,
    "column_4" VARCHAR(255) NOT NULL,
    "column_5" CHAR(1) NOT NULL,
    "column_6" INTEGER NOT NULL,
    "test_nf_data_no_header_id" INTEGER SERIAL NOT NULL,
    PRIMARY KEY ("test_nf_data_no_header_id")
);

-- NORMALIZATION SUGGESTIONS:
-- [3NF] test_nf_data_no_header: Transitive dependency detected: column_1 depends on column_3, creating transitive dependency through primary key. Consider extracting to a separate 'column_3_details' columns_and_types with columns: column_3, column_1.
--   Confidence: 1.0

-- [3NF] test_nf_data_no_header: Transitive dependency detected: column_2, column_6 depends on column_4, creating transitive dependency through primary key. Consider extracting to a separate 'column_4_details' columns_and_types with columns: column_4, column_2, column_6.
--   Confidence: 1.0

-- [3NF] test_nf_data_no_header: Transitive dependency detected: column_4, column_6 depends on column_2, creating transitive dependency through primary key. Consider extracting to a separate 'column_2_details' columns_and_types with columns: column_2, column_4, column_6.
--   Confidence: 1.0

-- [3NF] test_nf_data_no_header: Transitive dependency detected: column_3 depends on column_1, creating transitive dependency through primary key. Consider extracting to a separate 'column_1_details' columns_and_types with columns: column_1, column_3.
--   Confidence: 1.0
