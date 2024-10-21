package main

import (
    "context"
    "fmt"
    "log"
    "os"
    "path/filepath"
    "strings"

    "github.com/jackc/pgx/v4"
    "github.com/xitongsys/parquet-go-source/local"
    "github.com/xitongsys/parquet-go/reader"
)

type Data struct {
    curr_date 
    // Define your struct based on the Parquet schema
    // Example:
    // Field1 string `parquet:"name=field1, type=BYTE_ARRAY, convertedtype=UTF8"`
    // Field2 int32  `parquet:"name=field2, type=INT32"`
}

func main() {
    folderPath := "your/folder/path"
    tableName := "your_table_name"

    // PostgreSQL connection parameters
    connStr := "postgres://username:password@host:port/dbname"

    // Create PostgreSQL connection
    conn, err := pgx.Connect(context.Background(), connStr)
    if err != nil {
        log.Fatalf("Unable to connect to database: %v\n", err)
    }
    defer conn.Close(context.Background())

    // Scan folder for Parquet files
    files, err := filepath.Glob(filepath.Join(folderPath, "*.parquet"))
    if err != nil {
        log.Fatalf("Error scanning folder: %v\n", err)
    }

    // Process each Parquet file
    for _, file := range files {
        if err := processParquetFile(file, tableName, conn); err != nil {
            log.Printf("Failed to process file %s: %v\n", file, err)
        } else {
            fmt.Printf("Successfully processed file %s\n", file)
        }
    }
}

func processParquetFile(parquetFile, tableName string, conn *pgx.Conn) error {
    // Open Parquet file
    fr, err := local.NewLocalFileReader(parquetFile)
    if err != nil {
        return fmt.Errorf("can't open file: %v", err)
    }
    defer fr.PFile.Close()

    pr, err := reader.NewParquetReader(fr, new(Data), 4)
    if err != nil {
        return fmt.Errorf("can't create parquet reader: %v", err)
    }
    defer pr.ReadStop()

    num := int(pr.GetNumRows())
    data := make([]Data, num)
    if err := pr.Read(&data); err != nil {
        return fmt.Errorf("can't read parquet data: %v", err)
    }

    // Insert data into PostgreSQL
    for _, row := range data {
        // Adjust based on your struct fields
        _, err := conn.Exec(context.Background(), fmt.Sprintf("INSERT INTO %s VALUES ($1, $2)", tableName), row.Field1, row.Field2)
        if err != nil {
            return fmt.Errorf("insert failed: %v", err)
        }
    }
    return nil
}
