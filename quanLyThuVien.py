import hashlib
import getpass
import os
from datetime import datetime, timedelta
from turtledemo.penrose import start
import random

'''
# XÓA DỮ LIỆU FILE .TXT
def clear_files(*file_paths):
    for file_path in file_paths:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("")  # Ghi chuỗi rỗng để xóa dữ liệu
    print("Đã xóa toàn bộ dữ liệu trong các file:", ", ".join(file_paths))


# Gọi hàm và truyền vào danh sách các file cần xóa
clear_files(
    "books.txt",
    "borrowRequests.txt",
    "borrowRequestsCopy.txt",
    "customers.txt",
    "managers.txt",
    "rentHistory.txt",
    "trackingBooks.txt",
)
'''


# HÀM CHỨC NĂNG DÀNH CHO KHÁCH HÀNG
# Mượn sách
def borrow_book(username):
    titleToBorrow = input("Nhập tên sách muốn mượn: ")

    # Đọc thông tin từ file .txt
    books = []
    with open("books.txt", "r", encoding="utf-8") as file:
        for line in file:
            data = line.strip().split(",")
            books.append(data)

    # Lọc các sách có tên trùng với tên sách cần mượn
    matchingBooks = [book for book in books if titleToBorrow.lower() in book[1].lower()]

    if not matchingBooks:
        print("Không tìm thấy sách '" + titleToBorrow + "' trong hệ thống.")
        return

    # Hiển thị danh sách sách tìm được
    print("Các sách hiện có tại thư viện: ")
    for idx, book in enumerate(matchingBooks, start=1):
        print(
            f"{idx}. {book[1]}, Tác giả: {book[2]}, NXB: {book[3]}, Thể loại: {book[4]}, Số lượng còn lại: {book[7]}"
        )

    # Chọn sách và nhập số lượng mượn
    while True:
        try:
            choice = int(input("Chọn sách muốn mượn: "))
            if 1 <= choice <= len(matchingBooks):
                break
            else:
                print(f"Vui lòng chọn một số trong khoảng 1 đến {len(matchingBooks)}.")
        except ValueError:
            print("Vui lòng nhập một số hợp lệ.")

    chosenBook = matchingBooks[choice - 1]
    borrowAmount = int(input("Nhập số lượng muốn mượn: "))
    if borrowAmount <= 0 or borrowAmount > int(chosenBook[7]):
        print("Số lượng không hợp lệ.")
        return

    # Nhập số ngày mượn
    days = int(input("Nhập số ngày mượn: "))
    if days <= 0:
        print("Số ngày mượn không hợp lệ.")
        return

    # Tính ngày mượn và trả
    borrowDate = datetime.now().strftime("%d/%m/%Y")
    returnDate = (datetime.now() + timedelta(days=days)).strftime("%d/%m/%Y")

    # Sinh mã yêu cầu mượn sách
    request_code = generate_request_code()

    # Cập nhật mã yêu cầu mượn sách vào customers.txt nếu là yêu cầu đầu tiên
    customers = []
    customer_found = False
    with open("customers.txt", "r", encoding="utf-8") as file:
        for line in file:
            data = line.strip().split(",")
            if data[0] == username:
                customer_found = True
                if len(data) < 5 or data[4] == "":
                    data.append(request_code)  # Lưu mã mượn sách vào vị trí thứ 5
                else:
                    data[4] += f",{request_code}"
            customers.append(data)

    if not customer_found:
        print("Không tìm thấy tài khoản khách hàng.")
        return

    # Ghi lại cập nhật vào file customers.txt
    with open("customers.txt", "w", encoding="utf-8") as file:
        for customer in customers:
            file.write(",".join(customer) + "\n")

    # Cập nhật lại thông tin sách
    chosenBook[6] = str(int(chosenBook[6]) + borrowAmount)
    chosenBook[7] = str(int(chosenBook[7]) - borrowAmount)

    # Ghi lại thông tin vào file books.txt
    with open("books.txt", "w", encoding="utf-8") as file:
        for book in books:
            file.write(",".join(book) + "\n")

    # Ghi yêu cầu mượn sách vào borrowRequests.txt
    with open("borrowRequests.txt", "a", encoding="utf-8") as file:
        file.write(
            f"{request_code}, {chosenBook[0]}, {chosenBook[1]}, {chosenBook[2]}, {chosenBook[3]}, {borrowDate}, {returnDate}, {borrowAmount}, Pending\n"
        )

    # Ghi yêu cầu vào borrowRequestsCopy.txt với số thứ tự
    with open("borrowRequestsCopy.txt", "a", encoding="utf-8") as file:
        requests_copy = [
            line for line in open("borrowRequestsCopy.txt", "r", encoding="utf-8")
        ]
        order_number = len(requests_copy) + 1
        file.write(
            f"{order_number}, {chosenBook[0]}, {chosenBook[1]}, {chosenBook[2]}, {chosenBook[3]}, {borrowDate}, {returnDate}, {borrowAmount}, Pending\n"
        )

    print("Yêu cầu mượn sách đã được ghi lại. Đang chờ phê duyệt.")


# Trả sách
def return_book(username):
    global temp2, temp

    # Lấy các mã mượn sách của khách hàng từ file customers.txt
    customer_borrow_codes = []
    with open("customers.txt", "r", encoding="utf-8") as customer_file:
        for line in customer_file:
            data = line.strip().split(",")
            if data[0] == username:
                customer_borrow_codes = data[
                    4:
                ]  # Lấy mã mượn sách từ vị trí thứ 5 trở đi
                break

    if not customer_borrow_codes:
        print("Không tìm thấy mã khách hàng hoặc khách hàng chưa mượn sách.")
        return

    # Lọc và hiển thị các lệnh mượn sách của khách hàng từ borrowRequests.txt
    customer_requests = []
    with open("borrowRequests.txt", "r", encoding="utf-8") as borrow_file:
        requests = [line.strip().split(",") for line in borrow_file if line.strip()]
        for request in requests:
            if request[0] in customer_borrow_codes:
                customer_requests.append(request)

    if not customer_requests:
        print("Errored!")
        return

    # Hiển thị các lệnh mượn sách của khách hàng
    print("Danh sách lệnh mượn sách của bạn:")
    for idx, request in enumerate(customer_requests, start=1):
        print(
            f"{idx}. Mã mượn sách: {request[0]}, Tên sách: {request[2]}, Ngày mượn: {request[5]}, Số lượng: {request[7]}"
        )
        temp = int(request[7])
        temp2 = request[2].strip()

    # Cho khách hàng chọn lệnh muốn trả sách
    while True:
        try:
            selection = int(
                input("Nhập số thứ tự lệnh mượn sách muốn trả (hoặc 0 để thoát): ")
            )
            if selection == 0:
                print("Thoát trả sách.")
                return
            elif 1 <= selection <= len(customer_requests):
                break
            else:
                print(
                    f"Vui lòng chọn một số từ 1 đến {len(customer_requests)} hoặc 0 để thoát."
                )
        except ValueError:
            print("Vui lòng nhập một số hợp lệ.")

    selected_request = customer_requests[selection - 1]
    borrow_code = selected_request[0]  # Mã mượn sách đã chọn

    # Cập nhật trạng thái "Đã hoàn trả" trong rentHistory.txt
    with open("rentHistory.txt", "r", encoding="utf-8") as history_file:
        history_lines = history_file.readlines()

    with open("rentHistory.txt", "w", encoding="utf-8") as history_file:
        for line in history_lines:
            data = line.strip().split(",")
            if data[0] == borrow_code:
                # Cập nhật trạng thái "Đã hoàn trả" vào cuối dòng
                line = ",".join(data[:-1]) + ",Đã hoàn trả.\n"
            history_file.write(line)

    # Xóa lệnh mượn sách khỏi trackingBooks.txt
    with open("trackingBooks.txt", "r", encoding="utf-8") as tracking_file:
        tracking_lines = tracking_file.readlines()

    with open("trackingBooks.txt", "w", encoding="utf-8") as tracking_file:
        for line in tracking_lines:
            data = line.strip().split(",")
            if data[0] != borrow_code:
                tracking_file.write(line)

    # Xóa lệnh mượn sách khỏi borrowRequests.txt
    with open("borrowRequests.txt", "r", encoding="utf-8") as borrow_file:
        borrow_lines = borrow_file.readlines()

    with open("borrowRequests.txt", "w", encoding="utf-8") as borrow_file:
        for line in borrow_lines:
            data = line.strip().split(",")
            if data[0] != borrow_code:
                borrow_file.write(line)

    # Cập nhật lại số lượng sách
    with open("books.txt", "r", encoding="utf-8") as books_file:
        books = [
            line.strip().split(",") for line in books_file
        ]  # Đọc và tách các phần tử bằng dấu phẩy

    for book in books:
        if (
            book[1].strip() == temp2
        ):  # Kiểm tra nếu tên sách trùng với temp2 (sử dụng strip để loại bỏ khoảng trắng dư thừa)
            borrowed_quantity = int(book[6])
            available_quantity = int(book[7])

            # Cập nhật số lượng đã cho mượn và số lượng còn lại
            book[6] = str(borrowed_quantity - temp)
            book[7] = str(available_quantity + temp)
            break

    # Ghi lại toàn bộ dữ liệu vào books.txt
    with open("books.txt", "w", encoding="utf-8") as books_file:
        for book in books:
            books_file.write(", ".join(book) + "\n")

    print("Cập nhật số lượng sách thành công.")

    # Thông báo hoàn thành trả sách
    print(
        "Yêu cầu trả sách đã được chấp nhận, vui lòng để sách vào đúng vị trí trả sách."
    )


# Kiểm tra yêu cầu mượn sách
def borrowRequestHistory(username):
    # Kiểm tra xem file borrowRequests.txt có tồn tại không
    filename = "borrowRequests.txt"
    if not os.path.exists(filename):
        print("Không có yêu cầu mượn sách nào trong hệ thống.")
        return

    # Đọc file borrowRequests.txt để lấy các yêu cầu mượn sách
    with open("borrowRequests.txt", "r", encoding="utf-8") as file:
        requests = file.readlines()

    # Mở file customer.txt để lấy mã yêu cầu mượn sách của khách hàng
    with open("customers.txt", "r", encoding="utf-8") as file:
        customers = file.readlines()

    # Tìm mã yêu cầu mượn sách của khách hàng dựa trên username (số căn cước công dân)
    user_request_codes = []
    for customer in customers:
        data = customer.strip().split(",")
        if data[0] == username:
            user_request_codes = data[
                4:
            ]  # Mã yêu cầu mượn sách bắt đầu từ vị trí thứ 5

    if not user_request_codes:
        print("Không tìm thấy yêu cầu mượn sách nào cho tài khoản này.")
        return

    # Lọc các yêu cầu mượn sách có mã yêu cầu khớp với của khách hàng
    user_requests = [req for req in requests if req.split(",")[0] in user_request_codes]

    if not user_requests:
        print("Bạn chưa có yêu cầu mượn sách nào.")
    else:
        print("Danh sách yêu cầu mượn sách đã gửi:")
        for req in user_requests:
            print(req.strip())


# HÀM CHỨC NĂNG DÀNH CHO NHÂN VIÊN QUẢN LÝ
# Thêm sách vào hệ thống
def add_book():
    n = int(input("Nhập số lượng đầu sách cần thêm: "))

    # Tạo vòng lặp để nhập n đầu sách
    for i in range(1, n + 1):
        print("Nhập thông tin sách thứ " + str(i))
        bookID = input("- Mã sách: ")
        title = input("- Tên sách: ")
        author = input("- Tác giả: ")
        publisher = input("- Nhà xuất bản: ")
        genre = input("- Thể loại: ")
        totalQuantity = int(input("- Tổng số lượng sách: "))
        brrowedQuantity = 0
        availableQuantity = totalQuantity

        # Lưu thông tin vào file .txt
        with open("books.txt", "a", encoding="utf-8") as file:
            file.write(
                f"{bookID}, {title}, {author}, {publisher}, {genre}, {totalQuantity}, {brrowedQuantity}, {availableQuantity}\n"
            )
        print("Đã thêm sách '" + title + "' vào hệ thống.")


# Phê duyệt yêu cầu mượn sách
def approve_request():
    global borrow_code, customer_name
    with open("borrowRequests.txt", "r", encoding="utf-8") as file:
        requests = [line.strip().split(",") for line in file if line.strip()]

    if not requests:
        print("Không có yêu cầu mượn sách nào để phê duyệt.")
        return

    # Hiển thị danh sách yêu cầu mượn sách
    print("Danh sách yêu cầu mượn sách:")
    for idx, request in enumerate(requests, start=1):
        borrow_code = request[0]  # Mã mượn sách
        customer_name = "Không tìm thấy khách hàng"

        # Tìm tên khách hàng tương ứng với mã mượn sách
        with open("customers.txt", "r", encoding="utf-8") as file:
            for line in file:
                data = line.strip().split(",")
                borrow_codes = [code.strip() for code in data[4:]]

                if borrow_code in borrow_codes:
                    customer_name = data[1]
                    break

        # Hiển thị thông tin yêu cầu mượn sách
        print(
            f"{idx}. Mã mượn sách: {borrow_code}, Tên khách hàng: {customer_name}, "
            f"Tên sách: {request[2]}, Tác giả: {request[3]}, NXB: {request[4]}, "
            f"Ngày mượn: {request[5]}, Ngày trả: {request[6]}, Số lượng: {request[7]}, Trạng thái: {request[8]}"
        )

    # Lựa chọn yêu cầu để phê duyệt
    while True:
        try:
            selection = int(
                input("Nhập số thứ tự yêu cầu muốn phê duyệt (hoặc 0 để thoát): ")
            )
            if selection == 0:
                print("Thoát phê duyệt yêu cầu.")
                return
            elif 1 <= selection <= len(requests):
                break
            else:
                print(f"Vui lòng chọn một số từ 1 đến {len(requests)} hoặc 0 để thoát.")
        except ValueError:
            print("Vui lòng nhập một số hợp lệ.")

    # Lấy yêu cầu đã chọn
    selected_request = requests[selection - 1]

    # Phê duyệt hoặc từ chối yêu cầu
    approval = int(input("Phê duyệt yêu cầu mượn sách (1 - Đồng ý, 2 - Từ chối)?: "))
    new_status = "Đã phê duyệt" if approval == 1 else "Đã từ chối"
    selected_request[8] = f" {new_status}"

    # Cập nhật lại file borrowRequests.txt
    with open("borrowRequests.txt", "w", encoding="utf-8") as file:
        for req in requests:
            file.write(",".join(req) + "\n")

    # Nếu phê duyệt (Đồng ý), ghi vào trackingBooks.txt và rentHistory.txt
    if approval == 1:
        with open("trackingBooks.txt", "a", encoding="utf-8") as tracking_file, open(
            "rentHistory.txt", "a", encoding="utf-8"
        ) as history_file:
            tracking_data = f"{borrow_code},{customer_name},{selected_request[2]},{selected_request[3]},{selected_request[4]},{selected_request[5]},{selected_request[6]},{selected_request[7]}\n"
            history_data = f"{borrow_code},{customer_name},{selected_request[2]},{selected_request[3]},{selected_request[4]},{selected_request[5]},{selected_request[6]},{selected_request[7]}\n"

            tracking_file.write(tracking_data)
            history_file.write(history_data)

    print(f"Yêu cầu đã được {new_status}.")


# Chỉnh sửa thông tin sách
def edit_book():
    # Đọc toàn bộ nội dung file books.txt vào danh sách books
    books = []
    with open("books.txt", "r", encoding="utf-8") as file:
        for line in file:
            books.append(line.strip().split(", "))

    # Hiển thị tất cả các sách có trong file để người dùng chọn
    print("Danh sách sách hiện tại:")
    for i, book in enumerate(books, 1):
        print(f"{i}. Mã sách: {book[0]}, Tên sách: {book[1]}, Tác giả: {book[2]}")

    # Yêu cầu người dùng nhập mã sách muốn chỉnh sửa
    bookID_to_edit = input("Nhập mã sách cần chỉnh sửa: ")

    # Tìm sách cần chỉnh sửa trong danh sách books
    book_index = -1
    for index, book in enumerate(books):
        if book[0] == bookID_to_edit:
            book_index = index
            break

    if book_index == -1:
        print("Không tìm thấy sách với mã đã nhập.")
        return

    # Nhập thông tin mới
    print(f"Nhập lại thông tin sách mã {bookID_to_edit}:")
    title = input("- Tên sách: ")
    author = input("- Tác giả: ")
    publisher = input("- Nhà xuất bản: ")
    genre = input("- Thể loại: ")
    totalQuantity = int(input("- Tổng số lượng sách: "))
    borrowedQuantity = 0
    availableQuantity = totalQuantity

    # Thay thế thông tin cũ bằng thông tin mới
    books[book_index] = [
        bookID_to_edit,
        title,
        author,
        publisher,
        genre,
        str(totalQuantity),
        str(borrowedQuantity),
        str(availableQuantity),
    ]

    # Ghi lại toàn bộ nội dung vào file books.txt
    with open("books.txt", "w", encoding="utf-8") as file:
        for book in books:
            file.write(", ".join(book) + "\n")

    print(f"Đã cập nhật thông tin cho sách mã {bookID_to_edit}.")


# Xóa sách trong hệ thống
def delete_book():
    # Mở file books.txt và đọc toàn bộ danh sách sách vào list books
    with open("books.txt", "r", encoding="utf-8") as books_file:
        books = [line.strip().split(", ") for line in books_file]

    # Hiển thị toàn bộ sách hiện có trong hệ thống
    print("Danh sách sách hiện có trong hệ thống:")
    for idx, book in enumerate(books, start=1):
        print(
            f"{idx}. Mã sách: {book[0]}, Tên sách: {book[1]}, Tác giả: {book[3]}, Thể loại: {book[4]}, Tổng số lượng: {book[5]}, Số lượng đã mượn: {book[6]}, Số lượng còn lại: {book[7]}"
        )

    # Yêu cầu người dùng nhập vào mã sách muốn xóa
    book_code_to_delete = input("Nhập mã sách muốn xóa: ").strip()

    # Tìm sách có mã trùng với mã người dùng nhập
    book_found = False
    for book in books:
        if book[0].strip() == book_code_to_delete:  # Loại bỏ khoảng trắng khi so sánh
            books.remove(book)  # Xóa sách khỏi danh sách
            book_found = True
            break

    # Nếu không tìm thấy sách, thông báo lỗi
    if not book_found:
        print("Không tìm thấy mã sách trong hệ thống.")
        return

    # Ghi lại danh sách sách đã được cập nhật vào file books.txt
    with open("books.txt", "w", encoding="utf-8") as books_file:
        for book in books:
            books_file.write(", ".join(book) + "\n")

    # Thông báo thành công
    print(f"Sách có mã {book_code_to_delete} đã được xóa thành công.")


# HÀM CHUNG
# Mã hóa password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Lưu thông tin Khách Hàng và Người Quản Lý vào tệp .txt
def save_to_file(filename, data):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(data + "\n")


# Đăng kí tài khoản mới
def register_user(user_type):
    if user_type == "customer":
        filename = "customers.txt"
    elif user_type == "manager":
        filename = "managers.txt"
    else:
        print("Errored !")
        return

    id = input(
        "Nhập số căn cước công dân: "
        if user_type == "customer"
        else "Nhập mã nhân viên: "
    )
    fullName = input("Nhập họ và tên: ")
    email = input("Nhập địa chỉ Email: ")

    # Sử dụng vòng lặp để kiểm tra mật khẩu nhập vào
    while True:
        password = input("Nhập mật khẩu (Gồm ít nhất 8 kí tự): ")
        if len(password) >= 8:
            break
        else:
            print("Mật khẩu cần phải chứa ít nhất 8 kí tự. Vui lòng thử lại.")

    # Mã hóa mật khẩu sau khi đã nhập hợp lệ
    hashed_password = hash_password(password)

    # Lưu dữ liệu vào các tệp .txt'''
    data = f"{id},{fullName},{email},{hashed_password}"
    save_to_file(filename, data)
    print("Tài khoản đã được tạo thành công")


# Đăng nhập
def login(user_type):
    if user_type == "customer":
        filename = "customers.txt"
    elif user_type == "manager":
        filename = "managers.txt"
    else:
        print("Errored !")
        return False

    if not os.path.exists(filename):
        print("Tài khoản không tồn tại.")
        return False

    while True:
        username = input(
            "Nhập số căn cước công dân: "
            if user_type == "customer"
            else "Nhập mã nhân viên: "
        )
        password = input("Nhập mật khẩu (Gồm ít nhất 8 kí tự): ")
        hashed_password = hash_password(password)

        with open(filename, "r") as file:
            for line in file:
                data = line.strip().split(",")
                if data[0] == username and data[3] == hashed_password:
                    print("Đăng nhập thành công!")
                    return username
        print("Tên đăng nhập hoặc mật khẩu không đúng. Vui lòng thử lại.")


# Khôi phục tài khoản
def recovery(user_type):
    if user_type == "customer":
        filename = "customers.txt"
    elif user_type == "manager":
        filename = "managers.txt"
    else:
        print("Errored !")
        return

    # Yêu cầu xác thức tài khoản cần khôi phục
    id = input(
        "Nhập số Căn cước công dân: "
        if user_type == "customer"
        else "Nhập mã nhân viên: "
    )

    # Đọc nội dung trong các file .txt và chuyển sang lưu trữ trong danh sách
    with open(filename, "r") as file:
        lines = file.readlines()

    # Kiểm tra trong danh sách có tài khoản cần khôi phục hay không
    accountExists = False
    updated_lines = []

    for line in lines:
        data = line.strip().split(",")

        # Nếu tìm thấy tài khoản
        if data[0] == id:
            accountExists = True
            while True:
                newPassword = input("Nhập mật khẩu mới (Gồm ít nhất 8 kí tự): ")
                if len(newPassword) >= 8:
                    break
                else:
                    print("Mật khẩu cần phải chứa ít nhất 8 kí tự. Vui lòng thử lại.")

            # Mã hóa mật khẩu
            hashed_password = hash_password(newPassword)

            # Cập nhật thông tin tài khoản với mật khẩu mới
            data[3] = hashed_password
            updated_line = ",".join(data)
            updated_lines.append(updated_line + "\n")
        else:
            updated_lines.append(line)

        # Nếu tài khoản không tồn tại
        if not accountExists:
            print("Tài khoản không tồn tại.")
            return

        # Ghi lại các thông tin đã được cập nhật vào file
        with open(filename, "w") as file:
            file.writelines(updated_lines)

        print("Tài khoản đã được khôi phục thành công.")


# Hàm sinh mã yêu cầu mượn sách ngẫu nhiên
def generate_request_code():
    return str(random.randint(100000, 999999))


# Hàm tìm kiếm sách
def search_book():
    # Yêu cầu người dùng nhập tên sách cần tìm
    search_term = input("Nhập tên sách cần tìm: ").strip()

    # Đọc file books.txt và tìm sách
    found = False
    with open("books.txt", "r", encoding="utf-8") as books_file:
        books = [
            line.strip().split(",") for line in books_file
        ]  # Đọc và tách các phần tử bằng dấu phẩy

        # Duyệt qua danh sách sách và so sánh tên sách
        for book in books:
            book_name = book[1].strip()  # Tên sách tại vị trí thứ 1
            if (
                search_term.lower() in book_name.lower()
            ):  # So sánh tên sách (không phân biệt chữ hoa/thường)
                # In ra thông tin sách nếu tên sách trùng khớp
                print(
                    f"Mã sách: {book[0]}, Tên sách: {book[1]}, Tác giả: {book[2]}, NXB: {book[3]}, Thể loại: {book[4]}, Số lượng: {book[7]}"
                )
                found = True

    # Thông báo nếu không tìm thấy sách
    if not found:
        print("Không tìm thấy sách khớp với tên bạn đã nhập.")


def main_menu():
    while True:
        print("Main Menu")
        print("1 - Đăng nhập")
        print("2 - Đăng kí")
        print("3 - Thoát")
        choice = input("Lựa chọn 1 chức năng: ")
        print(" ")

        # Đăng nhập
        if choice == "1":
            print("Lựa chọn chức năng muốn sử dụng: ")
            print("1 - Đăng nhập dành cho khách hàng")
            print("2 - Đăng nhập dành cho nhân viên quản lý")
            print("3 - Khôi phục tài khoản")
            print("4 - Trở về Main menu")
            user_type = input("Bạn muốn sử dụng chức năng: ")
            print(" ")

            if user_type == "1":
                # DÀNH CHO KHÁCH HÀNG
                username = login("customer")
                if username:
                    while True:
                        print("Lựa chọn chức năng muốn sử dụng: ")
                        print("1 - Đăng kí mượn sách")
                        print("2 - Kiểm tra yêu cầu mượn sách")
                        print("3 - Đăng kí trả sách")
                        print("4 - Xem danh sách sách hiện có")
                        print("5 - Tìm kiếm sách")
                        print("6 - Đăng xuất")

                        customerChoice = input("Bạn muốn sử dụng chức năng: ")
                        if customerChoice == "1":
                            borrow_book(username)
                        elif customerChoice == "2":
                            borrowRequestHistory(username)
                        elif customerChoice == "3":
                            return_book(username)
                        elif customerChoice == "4":
                            with open("books.txt", "r", encoding="utf-8") as books_file:
                                books = books_file.readlines()

                            # In thông tin sách với các chú thích
                            for idx, book in enumerate(books, start=1):
                                book_info = book.strip().split(", ")

                                # Kiểm tra xem sách có đủ 8 trường thông tin không
                                if len(book_info) != 8:
                                    continue  # Bỏ qua dòng này nếu không đủ thông tin hoặc dòng trống

                                # In ra thông tin với các chú thích
                                print(
                                    f"{idx}. Mã sách: {book_info[0]}, Tên sách: {book_info[1]}, Tác giả: {book_info[2]}, NXB: {book_info[3]}, Thể loại: {book_info[4]}, Tổng số lượng: {book_info[5]}, Đang cho mượn: {book_info[6]}, Số lượng còn lại: {book_info[7]}"
                                )
                        elif customerChoice == "5":
                            search_book()
                        elif customerChoice == "6":
                            break  # Quay lại Main Menu
                        else:
                            print("Lựa chọn không hợp lệ, vui lòng thử lại.")

            elif user_type == "2":
                # DÀNH CHO NHÂN VIÊN
                username = login(
                    "manager"
                )  # Đăng nhập chỉ xảy ra khi người dùng chọn chức năng
                if username:  # Nếu đăng nhập thành công
                    while True:
                        print("Lựa chọn chức năng muốn sử dụng: ")
                        print("1 - Cập nhật sách mới")
                        print("2 - Kiểm tra yêu cầu mượn sách")
                        print("3 - Theo dõi sách đang cho mượn")
                        print("4 - Theo dõi lịch sử cho mượn sách")
                        print("5 - Thống kê số lượng sách của thư viện")
                        print("6 - Chỉnh sửa thông tin sách")
                        print("7 - Xóa sách khỏi hệ thống")
                        print("8 - Tìm kiếm sách")
                        print("9 - Đăng xuất")

                        employeeChoice = input("Bạn muốn sử dụng chức năng: ")
                        if employeeChoice == "1":
                            add_book()
                        elif employeeChoice == "2":
                            approve_request()
                        elif employeeChoice == "3":
                            with open(
                                "trackingBooks.txt", "r", encoding="utf-8"
                            ) as file:
                                data = file.readlines()

                            if not data:
                                print("Không có dữ liệu trong file trackingBooks.txt.")
                                return

                            print("Danh sách các sách đang được mượn:")
                            for line in data:
                                # Tách các thông tin theo định dạng lưu trữ trong file
                                (
                                    borrow_code,
                                    customer_name,
                                    book_title,
                                    author,
                                    publisher,
                                    borrow_date,
                                    return_date,
                                    quantity,
                                ) = line.strip().split(",")
                                print(
                                    f"{borrow_code},{customer_name},{book_title},{author},{publisher},{borrow_date},{return_date},{quantity}"
                                )
                        elif employeeChoice == "4":
                            try:
                                with open(
                                    "rentHistory.txt", "r", encoding="utf-8"
                                ) as file:
                                    content = file.readlines()

                                    if not content:
                                        print("Lịch sử cho mượn hiện đang trống.")
                                    else:
                                        print("Lịch sử cho mượn sách: ")
                                        for line in content:
                                            print(line.strip())

                            except FileNotFoundError:
                                print("Errored !")
                        elif employeeChoice == "5":
                            with open("books.txt", "r", encoding="utf-8") as books_file:
                                books = books_file.readlines()

                            # In thông tin sách với các chú thích
                            for idx, book in enumerate(books, start=1):
                                # Làm sạch dòng và chia tách
                                book_info = book.strip().split(",")

                                print(f"Dòng {idx}: {book_info}")

                                # In ra thông tin với các chú thích
                                print(
                                    f"{idx}. Mã sách: {book_info[0].strip()}, Tên sách: {book_info[1].strip()}, Tác giả: {book_info[2].strip()}, "
                                    f"NXB: {book_info[3].strip()}, Thể loại: {book_info[4].strip()}, Tổng số lượng: {book_info[5].strip()}, "
                                    f"Đang cho mượn: {book_info[6].strip()}, Số lượng còn lại: {book_info[7].strip()}"
                                )

                        elif employeeChoice == "6":
                            edit_book()
                        elif employeeChoice == "7":
                            delete_book()
                        elif employeeChoice == "8":
                            search_book()
                        elif employeeChoice == "9":
                            break
                        else:
                            print("Lựa chọn không hợp lệ, vui lòng thử lại.")

            elif user_type == "3":
                # Khôi phục tài khoản
                user_type = input(
                    "Khôi phục tài khoản cho (1 - Khách hàng, 2 - Nhân viên quản lý): "
                )
                if user_type == "1":
                    recovery("customer")
                elif user_type == "2":
                    recovery("manager")
                else:
                    print("Errored !")
                print(" ")
            elif user_type == "4":
                continue
            else:
                print("Errored !")

        # Đăng kí
        elif choice == "2":
            print("Lựa chọn chức năng muốn sử dụng: ")
            print("1 - Đăng kí tài khoản dành cho khách hàng")
            print("2 - Đăng kí tài khoản dành cho nhân viên quản lý")
            print("3 - Trở về Main Menu")
            user_type = input("Bạn muốn sử dụng chức năng: ")
            print(" ")

            if user_type == "1":
                register_user("customer")
            elif user_type == "2":
                register_user("manager")
            elif user_type == "3":
                continue
            else:
                print("Errored !")

        # Thoát chương trình
        elif choice == "3":
            print("Đang thoát chương trình...")
            break  # Dừng chương trình

        else:
            print("Lựa chọn không hợp lệ, vui lòng thử lại.")


main_menu()
