import fitz  # PyMuPDF

def extract_text_blocks_from_pdf(pdf_path: str, target_pages: list[int] = []):  # Нумерация с 0
    """
    Извлекает текстовые блоки с указанной страницы PDF
    
    Args:
        pdf_path: путь к PDF файлу
        target_page: номер страницы (начиная с 0)
    
    Returns:
        Список словарей с информацией о текстовых блоках
    """
    print(f"Целевые страницы: {target_pages}")
    target_pages.sort()

    doc = fitz.open(pdf_path)
    blocks_info = []
    print(f"Целевые страницы: {target_pages}")
    # Проверяем, существует ли запрашиваемая страница
    if target_pages:
        if target_pages[-1] >= len(doc):
            print(f"В PDF только {len(doc)} страниц (нумерация с 0), а требуется страница {target_pages[-1]}")
            doc.close()
            return blocks_info
    
    for page_number, page in enumerate(doc):
        # Извлекаем текстовые блоки
        if page_number in target_pages or target_pages == []:
            blocks = page.get_text("dict")["blocks"]
            for i, block in enumerate(blocks):
                if "lines" in block:  # Пропускаем блоки без текста (изображения и т.д.)
                    block_info = {
                        "block_number": i + 1,
                        "bbox": block["bbox"],  # Координаты блока [x0, y0, x1, y1]
                        "type": block["type"],
                        "text": "",
                        "lines_count": len(block["lines"]),
                        "spans": []
                    }
                    
                    # Собираем текст из всех строк блока
                    lines_text = []
                    for line in block["lines"]:
                        line_text = "".join(span["text"] for span in line["spans"])
                        lines_text.append(line_text)
                        
                        # Сохраняем информацию о спанах (форматирование)
                        for span in line["spans"]:
                            block_info["spans"].append({
                                "text": span["text"],
                                "font": span["font"],
                                "size": span["size"],
                                "color": span["color"],
                                "bbox": span["bbox"]
                            })
                    
                    block_info["text"] = "\n".join(lines_text)
                    blocks_info.append(block_info)
            
    doc.close()
    return blocks_info

def print_blocks_info(blocks_info):
    chosen_blocks = []
    """Выводит информацию о текстовых блоках"""
    for block in blocks_info:
        print(f"\n{'='*60}")
        print(f"БЛОК #{block['block_number']}")
        print(f"{'='*60}")
        print(f"Координаты: {block['bbox']}")
        print(f"Тип: {block['type']} (0-текст, 1-изображение)")
        print(f"Количество строк: {block['lines_count']}")
        print(f"Количество спанов: {len(block['spans'])}")
        print(f"\nТекст блока:")
        print(f"{'-'*40}")
        print(block['text'])
        print(f"{'-'*40}")
        
        if block['spans'] and block['block_number'] in ["2", "3", "4"]:
            print("\nПервый спан (пример форматирования):")
            first_span = block['spans'][0]
            print(f"  Текст: '{first_span['text']}'")
            print(f"  Шрифт: {first_span['font']}")
            print(f"  Размер: {first_span['size']}")
            print(f"  Цвет: {first_span['color']}")
            chosen_blocks.append(block['text'])

    return chosen_blocks

# Пример использования
if __name__ == "__main__":
    pdf_file = "/home/all-c/Загрузки/Отели_OCR.pdf"
    
    try:
        # Извлекаем блоки с 5-й страницы (индекс 4)
        print(f"Извлечение текстовых блоков с 6-й страницы (индекс 5)...")
        text_blocks = extract_text_blocks_from_pdf(pdf_file, target_pages=[])
        
        if text_blocks:
            print(f"\nНайдено {len(text_blocks)} текстовых блоков на странице 5:")
            print_blocks_info(text_blocks)
            
            # Дополнительная статистика
            total_spans = sum(len(block['spans']) for block in text_blocks)
            total_text_length = sum(len(block['text']) for block in text_blocks)
            print(f"\n{'='*60}")
            print(f"СТАТИСТИКА:")
            print(f"Всего блоков: {len(text_blocks)}")
            print(f"Всего спанов: {total_spans}")
            print(f"Общая длина текста: {total_text_length} символов")
        else:
            print("На указанной странице нет текстовых блоков или страница пуста.")
            
    except FileNotFoundError:
        print(f"Файл '{pdf_file}' не найден.")
