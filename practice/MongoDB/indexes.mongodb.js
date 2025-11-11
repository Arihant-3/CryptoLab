use("ecommerce");

// db.sales.find();
// db.sales.getIndexes();

// db.sales.createIndex({ quantity: 1 });
// db.sales.createIndex({ quantity: 2 });
// db.sales.createIndex({ any_name: 3 });
db.sales.getIndexes();

// If faster then why not always make index?
// No, because indexes take up space and slow down writes.
// Indexes are a trade-off between read performance and write performance/storage.
// Read operation 🔼 but write operation 🔽

