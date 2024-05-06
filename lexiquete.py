import os 
import nltk
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QMenu, QAction, QInputDialog
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase, QPalette, QBrush
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
from logic import count_words, remove_stopwords, get_word_frequency_table_data, get_word_details


class ResultWindow(QWidget):
    def __init__(self, word_count, cleaned_text, table_data):
        super().__init__()
        self.setWindowTitle("LexQuete Result")
        self.setGeometry(200, 200, 600, 400)
        self.setStyleSheet("background-color: #186ed3")
        self.original_table_data = table_data  # Store original table data
        self.current_table_data = table_data.copy() # Store current table data


        layout = QVBoxLayout()

        # Display word count
        word_count_label = QLabel(f"Word Count: {word_count}")
        word_count_label.setFont(QFont("BigNoodleTitling", 20))
        layout.addWidget(word_count_label)

        # Show word frequency table
        table_label = QLabel("Word Frequency Table:")
        table_label.setFont(QFont("BigNoodleTitling", 20))
        layout.addWidget(table_label)

        # Create a QTableWidget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)  # Three columns for Word, Frequency, Percentage
        self.table_widget.setHorizontalHeaderLabels(["Word", "Frequency", "Percentage"])

        # Populate the table with data
        self.populate_table(table_data)

        # Adjust column widths to fit content
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add the widget to the layout
        layout.addWidget(self.table_widget)

        # Normalize Button
        self.normalize_button = QPushButton("Normalize")
        self.normalize_button.clicked.connect(self.normalize_table)
        layout.addWidget(self.normalize_button)


         # Context menu for the table widget
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Search Button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.open_search_window)
        layout.addWidget(search_button)


        # Save Button
        self.save_button = QPushButton("Save Table")
        self.save_button.clicked.connect(self.save_table)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.cleaned_text = cleaned_text
           
    #to open the search window 
    def open_search_window(self):
        self.search_window = SearchWindow(self.cleaned_text, self)
        self.search_window.show()
    # Normalize the table data
    def normalize_table(self):
        lemmatizer = WordNetLemmatizer()
        self.current_table_data = [[lemmatizer.lemmatize(word.lower()), freq, perc] for word, freq, perc in self.current_table_data]
        self.populate_table(self.current_table_data)

# Show context menu for the table widget
    def show_context_menu(self, pos):
        row = self.table_widget.rowAt(pos.y())
        col = self.table_widget.columnAt(pos.x())
        if row >= 0 and col >= 0:
            menu = QMenu(self)
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.delete_row(row))
            modify_action = QAction("Modify", self)
            modify_action.triggered.connect(lambda: self.modify_cell(row, col))
            menu.addAction(delete_action)
            menu.addAction(modify_action)
            menu.exec_(self.table_widget.mapToGlobal(pos))

    def modify_cell(self, row, col):
        item = self.table_widget.item(row, col)
        if item is not None:
            new_value, ok = QInputDialog.getText(self, "Modify Cell", "Enter new value:")
            if ok:
                item.setText(new_value)
                self.current_table_data[row][col] = new_value
                self.reorder_table()

    def reorder_table(self):
        # Sort current table data based on frequency (second column)
        self.current_table_data.sort(key=lambda x: int(x[1]), reverse=True)
        total = sum(int(row[1]) for row in self.current_table_data)  # Calculate the total frequency
        for row in self.current_table_data:
            frequency = int(row[1])
            percentage = (frequency / total) * 100  # Calculate the new percentage
            row[2] = f"{percentage:.2f}%"  # Update the percentage in the current table data
        self.populate_table(self.current_table_data)

    
    def populate_table(self, data):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(len(data))
        for i, row_data in enumerate(data):
            for j, item_data in enumerate(row_data):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(item_data)))

    def delete_row(self, row):
        self.current_table_data.pop(row)
        self.populate_table(self.current_table_data)

    def save_table(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, 'Save Table', '', "CSV Files (*.csv)")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    for row_data in self.current_table_data:
                        file.write(','.join(row_data) + '\n')
                QMessageBox.information(self, "Save Successful", "Table saved successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Save Error", f"An error occurred while saving the table: {str(e)}")





class SearchWindow(QWidget):
    def __init__(self, cleaned_text, result_window):
        super(SearchWindow, self).__init__()
        self.cleaned_text = cleaned_text
        self.result_window = result_window  # Store the ResultWindow instance
        layout = QVBoxLayout()
        
        # Search bar
        self.search_bar = QLineEdit()
        layout.addWidget(self.search_bar)
        
        # Search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_word)
        layout.addWidget(search_button)
        
        # Result label
        self.result_label = QLabel()
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
        
        # Set the font, background color, and window size same as ResultWindow
        self.setFont(self.result_window.font())
        self.setStyleSheet("background-color: " + self.result_window.palette().window().color().name())
        self.resize(self.result_window.size())


    def search_word(self):
        word = self.search_bar.text()
        frequency, df, paragraph_ids, tf, average_tf_idf = get_word_details(word, self.cleaned_text)
        document_ids_str = ', '.join(map(str, paragraph_ids))  # Convert paragraph_ids to a comma-separated string
        result_text = f"Frequency: {frequency}\nDF Document Frequency: {df}\nDocument IDs: {document_ids_str}\nTF Term Frequency: {tf}\nRelevance TF-IDF: {average_tf_idf}"
        self.result_label.setText(result_text)
        self.result_label.setFont(QFont("BigNoodleTitling", 20))






class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("LexQuete")
        self.setGeometry(100, 100, 700, 500)
        self.setFixedSize(700, 500)
    
        background = QPixmap("assets/sky2.jpg").scaled(self.size())
        brush = QBrush(background)
        palette = QPalette()
        palette.setBrush(QPalette.Background, brush)
        
        # Set the palette and the font
        self.setPalette(palette)
        QFontDatabase.addApplicationFont("/Users/didou/Developer/Projects/LexiQuete/fonts/noodle.ttf")
      
        left_layout = QVBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap("assets/logo3.png")
        pixmap = pixmap.scaled(400, 400,)  
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo_label)

        text_label = QLabel("A L3 ISIL Project / Module RI / Group 5")
        text_label.setFont(QFont("BigNoodleTitling", 20))
        text_label.setStyleSheet("color: #0a3556")
        left_layout.addWidget(text_label)

        text_label2= QLabel("Developed by:\n● Ounissi Dhia eddine \n● Rasoul Anis \n● Serir Louai Abdelmouiz \n● Hadil med Chérif \n● Assia nezar kebaiLi \n● Kara nesrine \n")
        text_label2.setWordWrap(True)
        text_label2.setStyleSheet("font-size: 12px")
        text_label2.setStyleSheet("color: #16cbaf")
        left_layout.addWidget(text_label2)
        
     
        

        # Right Side
        right_layout = QVBoxLayout()
    
        big_text_label = QLabel("LexQuete is a text analyzing program that allows you \nto preform multiple operations on your selected file")
        big_text_label.setWordWrap(True)
        big_text_label.setContentsMargins(10, 60, 10, 0)
        big_text_label.setFont(QFont("BigNoodleTitling", 26))
        right_layout.addWidget(big_text_label)

        bigger_text_label = QLabel("Let's start by choosing a file \n(english .txt or .docx)")
        bigger_text_label.setWordWrap(True)
        bigger_text_label.setContentsMargins(0, 150, 0, 0)
        bigger_text_label.setFont(QFont("BigNoodleTitling", 22))
        bigger_text_label.setStyleSheet("color: #000000")
        right_layout.addWidget(bigger_text_label)

        choose_file_button = QPushButton("Choose File")
        choose_file_button.setStyleSheet("background-color: #f99e1a; color: white; font-size: 15px; padding: 10px 15px; border-radius: 10px; border: none;")
        choose_file_button.clicked.connect(self.choose_file)
        right_layout.addWidget(choose_file_button)

        
        
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        self.setLayout(main_layout)

    def choose_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open File', '', "Text Files (*.txt);;Word Files (*.docx)")
        if file_path:
            word_count = count_words(file_path)
            if isinstance(word_count, int):
                with open(file_path, 'r', encoding='utf-8') as file:
                    original_text = file.read()
                    cleaned_text = remove_stopwords(original_text)
                table_data = get_word_frequency_table_data(cleaned_text)  # Get table data as a list of lists
                self.result_window = ResultWindow(word_count, cleaned_text, table_data)
                self.result_window.show()
                


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

        
