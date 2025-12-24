import clipin

def test_windows_available_formats():
    formats = clipin.available_formats()
    print("Available Formats on Windows are : ", formats)

def output_everything_from_clipboard():
    result = clipin.paste()
    print("Clipboard Contents Dump:")
    for fmt, data in result.items():
        print(f"Format: {fmt}, Data Type: {type(data)}, Data (first 100 chars): {str(data)[:100]}")
        if isinstance(fmt, str):
            filename = f'clipboard_data_{fmt.replace("/", "_")}.bin'
        else:
            filename = f'clipboard_data_format_{fmt}.bin'
        with open(filename, 'wb') as f:
            if isinstance(data, str):
                f.write(data.encode('utf-8'))
            elif data is not None:
                f.write(data)

if __name__ == '__main__':
    test_windows_available_formats()
    # output_everything_from_clipboard()
    clipin.paste('image/png')