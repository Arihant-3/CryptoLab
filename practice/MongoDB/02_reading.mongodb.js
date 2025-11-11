use("ecommerce");

// Show all products
// db.products.find()

// db.products.find({"name": "Wireless Mouse"})
// db.products.find({ category: "Electronics" })

// db.products.find({ price: { $gt: 1000 } })

// db.products.find({ price: { $gte: 1000, $lte: 50000 } })

// db.products.find({ $or: [{ category: "Electronics" }, { stock: { $lt: 50 } }] })


// Show only createdAt 
// db.products.find({}, { createdAt: 1, _id: 0 })
// db.products.find({}, { name: 1, price: 1, _id: 0 })
// 1 -> include (show) this field in the output
// 0 -> exclude (don't show) this field in the output

// Sort the results 
// db.products.find().sort({ price: 1 }) // 1 -> ascending order
// db.products.find().sort({ price: -1 }) // -1 -> descending order

// db.products.find({}, { name : 1, _id : 0}).sort({ price: 1 })

// Pagination
db.products.find().sort({ price: -1 }).skip(1).limit(1)
// skip(n) -> skips the first n results
// limit(n) -> limits the output to n results
// Pagination example:
// Let say you want to paginate your website with 10 products per page, then you will do this:
// db.products.find().skip(0).limit(10)
// db.products.find().skip(10).limit(10)
// db.products.find().skip(20).limit(10)
