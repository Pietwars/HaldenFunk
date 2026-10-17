#pragma once
#include <stdint.h>
#include <stddef.h>
namespace disaster {
// Reserve one NUL byte in disaster-radio's 233-byte message storage.
inline bool validPublicUart(const uint8_t* p,size_t n) {
  if(!p || n<4 || n>232 || p[3]!='|' || (p[2]!='c' && p[2]!='b')) return false;
  for(size_t i=0;i<n;i++) if(!p[i]) return false;
  return true;
}
inline size_t uartChunkSize(uint16_t mtu,size_t remaining) {
  const size_t capacity=mtu>3?mtu-3:20;
  return remaining<capacity?remaining:capacity;
}
}
