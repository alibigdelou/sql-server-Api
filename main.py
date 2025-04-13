from fastapi import FastAPI, HTTPException, Query
from database import connection_string
import pyodbc
from pydantic import BaseModel
from typing import Optional

app = FastAPI()



class Customer(BaseModel):
    FirstName: str
    LastName: str
    Phone: str = None
    Email: str = None
    Address: str = None
    CustomerType: str = None

@app.get('/test')
def hell():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("select * from Properties")
    row = cursor.fetchone()
    return{"msg": row}


@app.post("/create-customer/")
async def create_customer(customer: Customer):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("use [uni];")
        cursor.execute("""
            INSERT INTO Customers (FirstName, LastName, Phone, Email, Address, CustomerType) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            customer.FirstName, customer.LastName, customer.Phone, customer.Email, customer.Address, customer.CustomerType)
        conn.commit()
        conn.close()
        return {"message": "Customer created successfully"}
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-visit/{visit_id}")
async def delete_visit(visit_id: int):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("use [uni];")
        cursor.execute("DELETE FROM Visits WHERE VisitID = ?", visit_id)
        conn.commit()
        conn.close()
        return {"message": "Visit deleted successfully"}
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/properties-with-address/")
async def get_properties_with_address():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("use [uni];")
        query = """
        SELECT p.PropertyID, p.PropertyType, p.Price, p.Status, a.City, a.Street, a.PostalCode 
        FROM Properties p
        JOIN Addresses a ON p.AddressID = a.AddressID
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            raise HTTPException(status_code=404, detail="No properties found with addresses.")

        properties = []
        for row in rows:
            properties.append({
                "PropertyID": row.PropertyID,
                "PropertyType": row.PropertyType,
                "Price": row.Price,
                "Status": row.Status,
                "City": row.City,
                "Street": row.Street,
                "PostalCode": row.PostalCode
            })

        return {"properties": properties}

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    


class SearchProperties(BaseModel):
    property_type: str = None
    min_price: float = None
    max_price: float = None
    status: str = None
    area: float = None
    number_of_rooms: int = None

class SearchProperties(BaseModel):
    property_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    status: Optional[str] = None
    area: Optional[float] = None
    number_of_rooms: Optional[int] = None

@app.post("/search-properties/")
async def search_properties(search_criteria: SearchProperties):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("use [uni];")
        query = "SELECT * FROM Properties WHERE 1=1"
        params = []

        if search_criteria.property_type:
            query += " AND PropertyType = ?"
            params.append(search_criteria.property_type)
        if search_criteria.min_price is not None:
            query += " AND Price >= ?"
            params.append(search_criteria.min_price)
        if search_criteria.max_price is not None:
            query += " AND Price <= ?"
            params.append(search_criteria.max_price)
        if search_criteria.status:
            query += " AND Status = ?"
            params.append(search_criteria.status)
        if search_criteria.area is not None:
            query += " AND Area = ?"
            params.append(search_criteria.area)
        if search_criteria.number_of_rooms is not None:
            query += " AND NumberOfRooms = ?"
            params.append(search_criteria.number_of_rooms)

        cursor.execute(query, params)
        properties = cursor.fetchall()

        if not properties:
            raise HTTPException(status_code=404, detail="No properties found.")

        conn.close()
        return {"properties": [dict(zip([column[0] for column in cursor.description], row)) for row in properties]}

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateProperty(BaseModel):
    property_id: int
    property_type: str
    price: float
    status: str
    area: float
    number_of_rooms: int
    address_id: int

@app.post("/update-property/")
async def update_property(update_data: UpdateProperty):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("use [uni];")
        query = """
        UPDATE Properties
        SET PropertyType = ?, Price = ?, Status = ?, Area = ?, NumberOfRooms = ?, AddressID = ?
        WHERE PropertyID = ?
        """
        cursor.execute(query, update_data.property_type, update_data.price, update_data.status, 
                       update_data.area, update_data.number_of_rooms, update_data.address_id, 
                       update_data.property_id)
        conn.commit()
   
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Property not found.")

        conn.close()
        return {"message": "Property updated successfully."}

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GetContractsByCustomer/{cuId}")
async def get_contract_by_customer(cuId: int):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor = conn.cursor()
        cursor.execute("use [uni];")
        query = "SELECT * from GetContractsByCustomer(?)"
        cursor.execute(query, cuId)
        result = cursor.fetchall()
        # print(result)
        if result:
            conn.close()
            return {"Customers": [dict(zip([column[0] for column in cursor.description], row)) for row in result]}
        else:
            raise HTTPException(status_code=404, detail="Function did not return a value.")

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GetCustomersWithRentalContracts")
async def get_customrt_with_rentalcont():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor = conn.cursor()
        cursor.execute("use [uni];")
        query = "SELECT * from GetCustomersWithRentalContracts()"
        cursor.execute(query)
        result = cursor.fetchall()
        # print(result)
        if result:
            conn.close()
            return {"Customers": [dict(zip([column[0] for column in cursor.description], row)) for row in result]}
        else:
            raise HTTPException(status_code=404, detail="Function did not return a value.")

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))



class PropertyInput(BaseModel):
    address_id: int
    property_type: str
    price: float
    status: str
    area: float
    number_of_rooms: int
    facilities: str

@app.post("/add-property/")
async def add_property(property: PropertyInput):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("use [uni];")
        query = """
        EXEC InsertProperty ?, ?, ?, ?, ?, ?, ?
        """
        cursor.execute(
            query,
            property.address_id,
            property.property_type,
            property.price,
            property.status,
            property.area,
            property.number_of_rooms,
            property.facilities
        )
        conn.commit()
        conn.close()

        return {"message": "Property added successfully."}

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/update-property-price/{prop_id}/{prop_price}")
async def add_property(prop_id, prop_price):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("use [uni];")
        query = """
        EXEC UpdatePropertyPrice ?, ?
        """
        cursor.execute(
            query,
            prop_id,
            prop_price
            )
        conn.commit()
        conn.close()

        return {"message": "Property updated successfully."}

    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=str(e))