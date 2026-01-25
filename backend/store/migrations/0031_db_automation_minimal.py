from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0030_pg_trgm_product_title_idx"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE OR REPLACE FUNCTION store_product_set_in_stock()\n"
                "RETURNS trigger AS $$\n"
                "BEGIN\n"
                "  IF NEW.stock_qty IS NULL OR NEW.stock_qty <= 0 THEN\n"
                "    NEW.stock_qty := COALESCE(NEW.stock_qty, 0);\n"
                "    NEW.in_stock := FALSE;\n"
                "  ELSE\n"
                "    NEW.in_stock := TRUE;\n"
                "  END IF;\n"
                "  RETURN NEW;\n"
                "END;\n"
                "$$ LANGUAGE plpgsql;\n"
                "\n"
                "DROP TRIGGER IF EXISTS trg_store_product_set_in_stock ON store_product;\n"
                "CREATE TRIGGER trg_store_product_set_in_stock\n"
                "BEFORE INSERT OR UPDATE OF stock_qty ON store_product\n"
                "FOR EACH ROW EXECUTE FUNCTION store_product_set_in_stock();\n"
            ),
            reverse_sql=(
                "DROP TRIGGER IF EXISTS trg_store_product_set_in_stock ON store_product;\n"
                "DROP FUNCTION IF EXISTS store_product_set_in_stock();\n"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "CREATE OR REPLACE PROCEDURE store_decrement_stock(p_product_id integer, p_qty integer)\n"
                "LANGUAGE plpgsql\n"
                "AS $$\n"
                "BEGIN\n"
                "  IF p_qty IS NULL OR p_qty <= 0 THEN\n"
                "    RETURN;\n"
                "  END IF;\n"
                "  UPDATE store_product\n"
                "  SET stock_qty = GREATEST(COALESCE(stock_qty, 0) - p_qty, 0),\n"
                "      in_stock = CASE WHEN GREATEST(COALESCE(stock_qty, 0) - p_qty, 0) > 0 THEN TRUE ELSE FALSE END\n"
                "  WHERE id = p_product_id;\n"
                "END;\n"
                "$$;\n"
            ),
            reverse_sql="DROP PROCEDURE IF EXISTS store_decrement_stock(integer, integer);\n",
        ),
        migrations.RunSQL(
            sql=(
                "CREATE OR REPLACE FUNCTION store_order_items_total(p_order_id integer)\n"
                "RETURNS numeric AS $$\n"
                "DECLARE\n"
                "  total numeric;\n"
                "BEGIN\n"
                "  SELECT COALESCE(SUM(COALESCE(sub_total, 0) + COALESCE(shipping_amount, 0)), 0)\n"
                "  INTO total\n"
                "  FROM store_cartorderitem\n"
                "  WHERE order_id = p_order_id;\n"
                "  RETURN total;\n"
                "END;\n"
                "$$ LANGUAGE plpgsql STABLE;\n"
            ),
            reverse_sql="DROP FUNCTION IF EXISTS store_order_items_total(integer);\n",
        ),
    ]
