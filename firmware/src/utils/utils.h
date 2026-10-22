#pragma once
#include <Arduino.h>
#include <stdio.h>

void hexToChar(char * out, unsigned char * in, size_t insz);
void charToHex(unsigned char * out, char * in, size_t outsz);

#include <stdlib.h>

// Zahl am Anfang von s lesen (fuehrende Leerzeichen erlaubt, wie sscanf "%d"/"%ld"/"%lf").
// Liefert fallback, wenn dort keine Zahl steht. Ersetzt sscanf: spart den scanf-Formatparser im Flash.
inline long parseLong(const char *s, long fallback)
{
  char *end;
  long v = strtol(s, &end, 10);
  return end == s ? fallback : v;
}
inline double parseDouble(const char *s, double fallback)
{
  char *end;
  double v = strtod(s, &end);
  return end == s ? fallback : v;
}
