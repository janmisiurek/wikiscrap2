# WikiScrap2


A simple table scraper from wikipedia pages with the ability to download them in the format of your choice. It has options to save tables on the server and edit tables like renaming and delete columns (only for registred users). I made this project for practice of flask, sqlalchemy and bootstrap.

## Requirements

- Python 3.x
- Flask
- Requests
- BeautifulSoup4
- Pandas
- Numpy
- Flask-SQLAlchemy
- OS
- Flask-Login
- IO

## Installation

1 Clone the repository:
```bash
git clone https://github.com/janmisiurek/wikiscrap2.git
```

2. install the required libraries:
```bash
pip install -r requirements.txt
```

## Run

1. navigate to the project folder:
```bash
cd wikiscrap2
```

2. launch the application:
```bash
python main.py
```
The application should now be available on `localhost:5000` (or another port if configured otherwise).

## License

This project is licensed under the MIT license - see the [LICENSE](LICENSE) file for details.
