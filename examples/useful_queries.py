QUERIES = {
    'table_exist': """
    SELECT EXISTS (
      SELECT 1
        FROM   information_schema.tables
        WHERE  table_schema = %s
        AND table_name = %s
    );
    """
}
