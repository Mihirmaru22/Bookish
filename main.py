from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from fastapi.responses import JSONResponse
from typing import Annotated, List, Optional
import json

app = FastAPI()


class Book(BaseModel):
    id: Annotated[
        str, Field(..., description="enter the book id here ", examples=["B001"])
    ]
    author: Annotated[str, Field(..., description="enter the book's auther here")]
    city: Annotated[
        Optional[str], Field(None, description="enter the author's home city here")
    ]
    pages: Annotated[
        Optional[int], Field(None, gt=0, description="enter the pages here")
    ]
    genre: Annotated[str, Field(..., description="enter the book genre here")]
    rating: Annotated[
        float, Field(..., ge=0, lt=5, description="enter the book rating here ")
    ]
    borrowed_by: Optional[str] = Field(None, description="ID of borrower if borrowed")
    borrowed_date: Optional[datetime] = Field(
        None, description="When book was borrowed"
    )
    due_date: Optional[datetime] = Field(
        None, description="When book should be returned"
    )


@computed_field
@property
def status(self) -> str:
    return "Borrowed" if self.borrowed_by else "Available"


def loadData():
    with open("books.json", "r") as f:
        data = json.load(f)
    return data


def save_data(data):
    with open("books.json", "w") as f:
        json.dump(data, f)


@app.get("/")
def welcome():
    return {"message": "welcome to my Bookish Api"}


@app.get("/about")
def about():
    return {"about": "this is about page of my Api"}


@app.get("/view")
def view():
    data = loadData()
    return data


@app.get("/book/{book_id}")
def view_book_detail(book_id: str):
    data = loadData()
    if book_id in data:
        return data[book_id]
    raise HTTPException(status_code=400, detail="book not found")


@app.get("/sort")
def sort_book(
    sort_by: str = Query(
        ..., description="sort by title , author , genre , rating , status"
    ),
    order: str = Query("asc", description="sort in asending or decenting order"),
):

    valid_field = ["title", "author", "genre", "rating", "status"]

    if sort_by not in valid_field:
        raise HTTPException(
            status_code=400, detail=f"invalid field select from {valid_field}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, detail="invalid order selecte between asc or desc"
        )

    data = loadData()
    sort_order = True if order == "desc" else False

    sort_data = sorted(
        data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order
    )

    return sort_data


@app.post("/add")
def create_request(book: Book):
    data = loadData()

    if book.id in data:
        exist_book = data[book.id]
        raise HTTPException(
            status_code=201,
            detail={"message": "book is in database", "book_detail": exist_book},
        )
    data[book.id] = book.model_dump(exclude={"id"}, exclude_none=True)

    save_data(data)
    return JSONResponse(
        status_code=201, content={"message": "book created sucessfully"}
    )
