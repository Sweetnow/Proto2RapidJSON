#include <fstream>
#include "proto.h"
#include "rapidjson/document.h"

int main(int argc, char *argv[])
{
    if (argc <= 1)
    {
        exit(EXIT_FAILURE);
    }
    std::ifstream fin(argv[1]);
    std::string json((std::istreambuf_iterator<char>(fin)),
                     std::istreambuf_iterator<char>());
    proto::Main m;
    m.Parse(json.c_str());
    return 0;
}