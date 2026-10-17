#include <assert.h>
#include <string.h>
#include <initializer_list>
#include "../firmware/src/client/OpenUart.h"
int main(){
  uint8_t p[234];memset(p,'x',sizeof(p));p[2]='c';p[3]='|';
  assert(!disaster::validPublicUart(nullptr,5));
  for(size_t n=0;n<4;n++)assert(!disaster::validPublicUart(p,n));
  assert(disaster::validPublicUart(p,4));assert(disaster::validPublicUart(p,232));
  assert(!disaster::validPublicUart(p,233));assert(!disaster::validPublicUart(p,234));
  p[2]='b';assert(disaster::validPublicUart(p,20));
  for(uint8_t type: {'i','u','/','r'}){p[2]=type;assert(!disaster::validPublicUart(p,20));}
  p[2]='c';p[10]=0;assert(!disaster::validPublicUart(p,20));p[10]='x';
  p[3]='!';assert(!disaster::validPublicUart(p,20));
  assert(disaster::uartChunkSize(23,232)==20);assert(disaster::uartChunkSize(260,232)==232);
  assert(disaster::uartChunkSize(23,3)==3);assert(disaster::uartChunkSize(23,0)==0);
}
