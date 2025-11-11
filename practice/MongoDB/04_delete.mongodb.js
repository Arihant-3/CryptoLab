use("ecommerce");

// Delete a single contact by name
// db.contacts.deleteOne({ name: "Bob" } );

// Delete multiple order with status pending
db.orders.deleteMany({ status: "Pending" } );