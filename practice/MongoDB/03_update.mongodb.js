use("ecommerce");

// Update the price of wireless mouse to 899 from 799
// db.products.updateOne(
//     { name: "Wireless Mouse"},
//     { $set : { price: 899 } }
// )

// Increase stock of all products in category "Electronics" by 10
// db.products.updateMany(
//     { category: "Electronics" },
//     { $inc: { stock: 10 } }
// )

// Adding a new tag i.e. array field to wireless mouse products
// $push operator is used to add a new element to an array field
db.products.updateMany(
    { name : "Wireless Mouse" },
    { $push: { tags: "Mouse" } }
)