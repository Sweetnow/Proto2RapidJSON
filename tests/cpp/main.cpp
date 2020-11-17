#include <iostream>
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
    m.FromString(json.c_str());
    auto s = m.ToString();
    std::cout << s << std::endl;
    s = m.ToPrettyString();
    std::cout << s << std::endl;
    return 0;
}