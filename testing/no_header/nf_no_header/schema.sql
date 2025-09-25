-- Generated DDL for postgresql
-- Generated at: 2025-09-25T10:28:28.603551

CREATE TABLE "test_nf_data_no_header" (
    "column_1" INTEGER NOT NULL,
    "column_2" VARCHAR(255) NOT NULL,
    "column_3" VARCHAR(255) NOT NULL,
    "column_4" VARCHAR(255) NOT NULL,
    "column_5" CHAR(1) NOT NULL,
    "column_6" INTEGER NOT NULL,
    PRIMARY KEY ("column_1", "column_2")
);

-- NORMALIZATION SUGGESTIONS:
-- [2NF] test_nf_data_no_header: Column 'column_3' has partial dependency on 'column_1' (part of composite key ['column_1', 'column_2']) instead of depending on the full key (strength: 100.0%). Consider extracting to a separate 'column_1_column_3' table with columns: column_1, column_3.
--   Confidence: 1.0

-- [2NF] test_nf_data_no_header: Column 'column_4' has partial dependency on 'column_2' (part of composite key ['column_1', 'column_2']) instead of depending on the full key (strength: 100.0%). Consider extracting to a separate 'column_2_column_4' table with columns: column_2, column_4.
--   Confidence: 1.0

-- [2NF] test_nf_data_no_header: Column 'column_6' has partial dependency on 'column_2' (part of composite key ['column_1', 'column_2']) instead of depending on the full key (strength: 100.0%). Consider extracting to a separate 'column_2_column_6' table with columns: column_2, column_6.
--   Confidence: 1.0
