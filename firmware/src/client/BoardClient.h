#ifndef BOARDCLIENT_H
#define BOARDCLIENT_H
// Schwarzes Brett: dauerhafte Aushaenge, ueber LoRa als Datagramm-Typ 'b' verteilt.
// Eingabe aus der Weboberflaeche kommt als lokaler Typ 'B' (wird nicht direkt gefunkt).
// Nutzlast: <ID 2 Byte>b|<post-id 8 hex>|<flags>|<Restminuten>|<Name>|<Text>
#include <Arduino.h>
#include <vector>
#include <FS.h>
#include "../DisasterClient.h"

#define BOARD_MAX_POSTS 30
#define BOARD_MAX_TTL_MIN (7 * 24 * 60)
#define BOARD_DEFAULT_TTL_MIN (24 * 60)
#define BOARD_TYPE_LORA 'b'
#define BOARD_TYPE_LOCAL 'B'

struct BoardPost
{
    String id;
    String flags;          // "P" = wichtig/angeheftet, "-" = normal
    uint32_t expiresAt;    // millis()
    String name;
    String text;
    uint32_t receivedAt;
    bool rebroadcastPending = false;
    uint32_t rebroadcastAt = 0;
};

class BoardClient : public DisasterClient
{
public:
    BoardClient(fs::FS *fs, const char *path = "/board.txt") : _fs(fs), _path(path) {}
    void setup();
    void loop();
    void receive(struct Datagram datagram, size_t len);
    String toJson();
    size_t count() const { return _posts.size(); }
    const BoardPost *at(size_t index) const { return index < _posts.size() ? &_posts[index] : nullptr; }

private:
    fs::FS *_fs;
    const char *_path;
    std::vector<BoardPost> _posts;
    uint32_t _lastSave = 0, _lastSync = 0, _lastExpiry = 0;
    size_t _syncIdx = 0;
    bool _dirty = false;
    bool parse(const char *payload, size_t len, BoardPost &out, uint32_t &ttlMin);
    int find(const String &id);
    void add(BoardPost &p);
    void send(BoardPost &p);
    void expire();
    void load();
    void save();
};
#endif
