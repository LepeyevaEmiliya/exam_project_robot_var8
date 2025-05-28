#include <windows.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>

using namespace std;

const char MARKER[] = "SECRET_START_2025"; 
const size_t MARKER_SIZE = sizeof(MARKER) - 1;

int main() {
    // Получаем путь к самому exe
    char path[MAX_PATH];
    GetModuleFileNameA(NULL, path, MAX_PATH);

    // Открываем файл exe для чтения
    ifstream file(path, ios::binary | ios::ate);
    if (!file) {
        cerr << "Cannot open executable file\n";
        return 1;
    }

    streamsize size = file.tellg();
    if (size < (streamsize)(MARKER_SIZE + 4)) {
        cerr << "File too small to contain secret\n";
        return 1;
    }

    // Считываем последние байты для поиска маркера
    // Минимум  marker + 4 байта длины + секрет (до 10 000 байт)
    const int max_secret_len = 10000;
    int read_size = MARKER_SIZE + 4 + max_secret_len;
    if (read_size > size) read_size = (int)size;

    file.seekg(size - read_size, ios::beg);
    vector<char> buffer(read_size);
    file.read(buffer.data(), read_size);

    // Ищем маркер с конца
    int pos = -1;
    for (int i = read_size - MARKER_SIZE - 4; i >= 0; --i) {
        if (memcmp(buffer.data() + i, MARKER, MARKER_SIZE) == 0) {
            pos = i;
            break;
        }
    }

    if (pos == -1) {
        cerr << "Secret marker not found\n";
        return 1;
    }

    // После маркера идут 4 байта - длина секрета (little endian)
    if (pos + MARKER_SIZE + 4 > read_size) {
        cerr << "Corrupted secret length\n";
        return 1;
    }

    uint32_t secret_len = 0;
    memcpy(&secret_len, buffer.data() + pos + MARKER_SIZE, 4);

    if (secret_len > max_secret_len || secret_len > (uint32_t)(read_size - pos - MARKER_SIZE - 4)) {
        cerr << "Invalid secret length\n";
        return 1;
    }

    string secret(buffer.data() + pos + MARKER_SIZE + 4, secret_len);

    // Выводим секрет
    cout << "Embedded secret:\n";
    cout << secret << "\n";

    system("pause");
    return 0;
}
