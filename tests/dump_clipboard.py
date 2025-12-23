import clipin

def test_windows_available_formats():
    formats = clipin.available_formats()
    print("Available Formats on Windows are : ", formats)

def output_everything_from_clipboard():
    result = clipin.paste()
    for fmt, data in result.items():
        print(f"Format: {fmt}, Data Type: {type(data)}, Data (first 100 chars): {str(data)[:100]}")
        with open(f'clipboard_data_{fmt.replace("/", "_")}.bin', 'wb') as f:
            if isinstance(data, str):
                f.write(data.encode('utf-8'))
            else:
                f.write(data)

if __name__ == '__main__':
    test_windows_available_formats()
    output_everything_from_clipboard()