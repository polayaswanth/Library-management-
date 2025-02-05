from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, Member, Book, BorrowedBook
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import date
  
  
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MemberCreate(BaseModel):
    name: str
    password: str
    role: str = "member"

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str

class BorrowBookRequest(BaseModel):
    member_id: int
    book_id: int
    return_date: date

class ReturnBookRequest(BaseModel):
    member_id: int
    book_id: int

@app.post("/register/")
def register_member(member: MemberCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(member.password)
    new_member = Member(name=member.name, password=hashed_password, role=member.role)
    db.add(new_member)
    db.commit()
    return {"message": "Member registered successfully"}

@app.post("/login/")
def login_member(name: str, password: str, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.name == name).first()
    if not member or not pwd_context.verify(password, member.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"member_id": member.id, "role": member.role}

@app.post("/books/")
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = Book(**book.dict())
    db.add(new_book)
    db.commit()
    return {"message": "Book added successfully"}

@app.get("/books/list/")
def list_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

@app.post("/borrow/")
def borrow_book(request: BorrowBookRequest, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == request.book_id, Book.available == True).first()
    if not book:
        raise HTTPException(status_code=400, detail="Book not available")
    
    book.available = False
    book.borrowed_by = request.member_id
    book.return_date = request.return_date

    borrowed = BorrowedBook(member_id=request.member_id, book_id=request.book_id, borrow_date=date.today(), return_date=request.return_date)
    db.add(borrowed)
    db.commit()
    
    return {"message": "Book borrowed successfully"}

@app.get("/borrowed_books/{member_id}/")
def get_borrowed_books(member_id: int, db: Session = Depends(get_db)):
    borrowed_books = db.query(BorrowedBook).filter(BorrowedBook.member_id == member_id).all()
    borrowed_books_data = []
    
    for borrowed in borrowed_books:
        book = db.query(Book).filter(Book.id == borrowed.book_id).first()
        borrowed_books_data.append({
            "book_id": borrowed.book_id,
            "title": book.title,
            "return_date": borrowed.return_date
        })
    
    return borrowed_books_data


@app.post("/return/")
def return_book(request: ReturnBookRequest, db: Session = Depends(get_db)):
    borrowed_book = db.query(BorrowedBook).filter(
        BorrowedBook.member_id == request.member_id,
        BorrowedBook.book_id == request.book_id
    ).first()

    if not borrowed_book:
        raise HTTPException(status_code=400, detail="Invalid return request")

    book = db.query(Book).filter(Book.id == request.book_id).first()
    book.available = True
    db.commit()

    db.delete(borrowed_book)
    db.commit()

    return {"message": "Book returned successfully, and record cleared"}
