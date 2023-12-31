# e_commerce
1. `/create-customer`\
HTTP method: POST\
Payload: 
`{
    "phone_number": "1234567890",
    "name": "Your name",
    "city": "Your city"
}`\
Edge Cases Covered:\
     a. Handling missing fields.\
     b. Checking for existing customers with the same phone number.\
     c. Thorough validation of name, city, and phone number (length and special characters).
![Screenshot from 2023-08-30 19-58-48](https://github.com/raashi11/image/assets/59081843/00a1495d-2492-4c7f-bfe6-4e6af7bc3564)

#
2. `/create-order`\
HTTP method: `POST`\
Payload:
`{
    "item_name": "Item's Name",
    "customer_phone": "1234567890"
}`\
Edge Cases Covered:\
     a. Handling missing fields.\
     b. Verifying customer existence.\
     c. Employing enums for consistent status representation.

![Screenshot from 2023-08-30 20-00-22](https://github.com/raashi11/image/assets/59081843/3fa7fac6-5881-45fc-b935-5868f26515bf)

#            
3. `/update-order-status`\
HTTP method: `PATCH`\
Payload:
`{
    "order_id": 1,
    "new_status": "Delivered"
}`\
Edge Cases Covered:\
    a. Handling missing fields.\
    b. Ensuring valid status values['Pending', 'Processing', 'Delivered'].

![Screenshot from 2023-08-30 20-02-58](https://github.com/raashi11/image/assets/59081843/e40170e1-9bc1-4c54-9b3c-ee3addc7434e)

#            
4. `/fetch-orders-by-city`\
HTTP method: `GET`\
Parameter: `/fetch-orders-by-city?city=Delhi`\
Edge Cases Covered:\
     a. Handling missing fields.\
     b. Detecting an unknown city.\
     c. Managing an empty city name.\
     d. Checking for orders within the specified city.

![Screenshot from 2023-08-30 20-04-55](https://github.com/raashi11/image/assets/59081843/592925e9-4a36-4cda-840f-1126d740f705)

