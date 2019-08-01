#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-01-14 14:43:31
# @Author  : dongchuan QQ:250212415
# @Version : v1.0
# @Desc    : SQL注入payload词法分词器
from tokens import *


sqlUpperToLower = [0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17,18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53,54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122,  91,  92,  93,  94,  95,  96,  97,  98,  99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197,  198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255]
sqlIsEbcdicIdChar = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0,0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1,0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0,]

aCode = [56, 115, 134, 34, 73, 36, 95, 44, 29, 104, 38, 39, 42, 2, 41, 137, 33, 21, 110, 14, 89, 132, 11, 103, 133, 108, 6, 98, 89, 135, 48, 9, 17, 90, 109, 52, 96, 94, 3, 28, 120, 119, 100, 18, 18, 60, 5, 89, 57, 63, 66, 16, 92, 42, 30, 27, 99, 130, 84, 13, 58, 35, 8, 114, 101, 43, 4, 26, 47, 24, 124, 55, 121, 131, 122, 49, 25, 50, 61, 91, 97, 136, 64, 31, 138, 10, 32, 89, 58, 58, 93, 7, 111, 62, 105, 37, 113, 89, 42, 116, 15, 123, 46, 45, 102, 65, 118, 89, 89, 12, 51, 106, 117, 53, 54, 40, 107, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729]
aHash = [[65, 611], [94, 135, 191, 305, 363, 401, 505, 514, 520, 674], [110, 128, 285, 345, 432, 668, 690], [63, 172, 233, 308, 399, 405, 490, 501, 543], [0, 154, 188, 234, 341, 442, 456, 616, 677], [44, 453, 532], [0, 597], [0, 164], [71, 151, 187, 189, 229, 331], [0, 124, 141, 162, 202, 624], [66, 148, 153, 312, 334, 437, 472, 549, 562, 587], [0, 412, 672], [0, 495, 516, 550, 589, 664], [104, 304, 358, 441, 485], [12, 387, 663], [67, 175, 225, 227, 414, 581, 588, 691], [15, 606], [0, 140, 454, 460, 647], [108, 136, 204, 275, 406, 427, 644], [74, 242, 639], [105, 235, 249, 359, 450, 464, 474, 496, 537, 547, 557, 655, 670], [101, 263, 320, 365, 507, 659], [0, 144, 368, 392, 479, 613], [19, 133, 256, 293, 302, 339, 443, 529, 667], [0, 146, 593, 598], [0, 170, 247, 291, 447, 451, 470, 584, 625], [114, 118, 266, 344, 352, 448, 599, 649], [0, 314, 459], [112, 232, 279, 326, 332, 555], [78, 333, 421], [0, 147, 149, 210, 260, 438, 617, 689], [22, 165, 169, 318, 433, 563, 575], [82, 212, 385, 527, 539, 540, 560], [0, 142], [9, 255, 276, 396], [0, 393, 455], [0, 391, 424], [59, 265, 502, 650], [60, 209, 366, 372], [0, 181, 530, 635, 676], [58, 180, 245, 286, 578, 594], [6, 284, 383, 398, 471, 554, 618, 679], [0, 137, 217, 248, 375, 458], [39, 600], [79, 340, 348, 428, 544], [91, 127, 329, 500, 541, 675, 684], [0, 262, 678], [111, 239, 295, 519], [90, 129, 213, 280, 343, 440, 558], [0, 309], [0, 261, 310, 364, 614], [45, 130, 250, 369, 652], [0, 283, 403, 511], [92, 183, 381, 388], [24, 328], [0, 542, 579], [17, 195, 230, 240, 246, 376, 565], [0, 294, 330, 355], [115, 252, 269, 585], [40, 158, 384, 595], [23, 167, 244, 268, 357], [0, 121], [5, 415, 417], [99, 120, 601, 602], [25, 254, 338], [85, 409], [0, 166, 176, 306, 574, 576], [0, 382, 654], [117, 323, 407, 465, 480, 660], [95, 270, 623], [50, 371, 573], [116, 122, 231], [47, 160, 192, 241, 400, 504], [7, 657], [42, 619], [0, 418, 523, 651], [80, 184, 510, 570, 642], [0, 186, 194, 271, 273, 370, 483, 515, 552, 673], [89, 156, 163], [26, 347, 423], [0, 218, 367, 551, 680], [88, 298, 301, 395, 508], [0, 243], [0, 408, 561, 592], [0, 145, 155, 362, 661], 84, [81, 177, 484, 533, 572], [86, 258, 319, 669], [77, 143, 205, 220, 238, 394, 425, 604, 626], [98, 139, 272, 475, 546], [14, 322, 457], [34, 482, 499, 681], [97, 553], [0, 253, 445, 591], [70, 125, 138, 199, 311, 313, 666], [0, 174, 259, 274, 346, 487, 630], [18, 152, 373, 431], [76, 131, 203, 207, 420, 466, 486, 621], [100, 228, 351, 380, 411, 462, 494, 497, 607], [31, 132, 222, 374, 377, 386, 413, 545, 653], [0, 219, 353, 402, 404, 410, 461, 528, 685], [113, 119, 159, 290, 297, 303, 361, 531, 645], [69, 123, 173, 206, 327, 356, 463, 468, 498, 583], [106, 288, 315, 324, 337, 419, 449, 473, 512, 580, 590, 648, 688], [52, 150, 237, 317, 360, 478, 481, 556, 612, 643], [46, 168, 190, 211, 216, 221, 264, 289, 390, 513, 536, 638, 662], [73, 609, 637], [0, 236, 349, 489, 603, 605, 608, 636], [0, 179, 193, 452, 538, 632, 634, 641], [83, 307, 444, 656, 686], [102, 157, 223, 278, 429, 434, 567, 577, 665], [0, 134, 178, 201, 251, 292, 534, 559], [109, 300, 325, 389, 422, 426, 439, 522, 525, 582, 640], [0, 196, 198, 214, 350, 467, 622, 683], [35, 267, 281, 299, 436, 446, 503, 682], [0, 126, 171, 224, 354, 566, 631], [0, 182, 200, 335, 569, 671], [28, 257, 615], [0, 282, 397, 476, 491, 509, 535, 571, 610, 629], [75, 321, 336, 379, 469, 518, 628, 646], [48, 316, 521, 548, 633], [53, 215, 226, 430, 492, 526, 568, 586, 658], [0, 208], [20, 161, 185, 296, 517, 627, 687], [51, 197, 287, 342, 416, 435, 488, 506, 524, 564], [0, 493, 620], [43, 277, 378, 477, 596]]
aLen = [7, 7, 5, 4, 6, 4, 5, 3, 6, 7, 3, 6, 6, 7, 7, 3, 8, 2, 6, 5, 4, 4, 3, 10, 4, 6, 11, 2, 7, 5, 5, 9, 6, 10, 9, 7, 10, 6, 5, 6, 6, 5, 6, 4, 9, 2, 5, 5, 6, 7, 7, 3, 4, 4, 7, 3, 6, 4, 7, 6, 12, 6, 9, 4, 6, 5, 4, 7, 6, 5, 6, 7, 5, 4, 5, 7, 5, 8, 3, 7, 13, 2, 2, 4, 6, 6, 8, 5, 17, 12, 7, 8, 8, 2, 4, 4, 4, 4, 4, 2, 2, 4, 6, 2, 3, 6, 5, 5, 5, 8, 3, 5, 5, 6, 4, 9, 3, 5, 7, 17, 7, 8, 6, 4, 8, 15, 15, 12, 12, 5, 14, 5, 7, 13, 7, 11, 3, 5, 4, 26, 12, 8, 7, 7, 2, 7, 7, 6, 6, 3, 12, 3, 15, 8, 4, 5, 22, 5, 4, 3, 6, 4, 17, 4, 8, 27, 7, 8, 6, 8, 8, 8, 8, 11, 6, 7, 5, 9, 8, 10, 6, 7, 13, 6, 25, 12, 9, 10, 5, 4, 8, 8, 5, 10, 7, 7, 3, 10, 10, 12, 17, 4, 4, 6, 7, 8, 4, 3, 5, 10, 4, 8, 12, 9, 3, 11, 9, 7, 3, 7, 7, 7, 5, 7, 5, 4, 7, 14, 5, 8, 10, 4, 8, 10, 3, 9, 4, 9, 4, 8, 8, 8, 11, 4, 7, 4, 8, 22, 10, 3, 10, 4, 9, 16, 6, 9, 8, 16, 3, 10, 5, 14, 5, 7, 7, 7, 9, 20, 9, 8, 4, 6, 8, 6, 5, 10, 3, 11, 3, 12, 5, 4, 4, 11, 10, 5, 4, 5, 7, 7, 20, 14, 12, 7, 3, 5, 5, 10, 10, 12, 5, 7, 7, 7, 11, 5, 9, 14, 3, 9, 8, 5, 7, 10, 5, 8, 4, 9, 12, 7, 9, 5, 5, 5, 24, 7, 6, 10, 8, 12, 7, 5, 8, 9, 10, 9, 6, 11, 6, 8, 7, 4, 12, 7, 7, 4, 6, 6, 11, 15, 12, 4, 4, 6, 7, 14, 10, 6, 4, 7, 11, 7, 7, 6, 10, 6, 11, 4, 5, 10, 7, 5, 2, 6, 8, 7, 8, 14, 17, 14, 13, 11, 17, 10, 9, 7, 3, 4, 8, 7, 8, 6, 9, 3, 5, 8, 10, 9, 10, 9, 15, 7, 7, 4, 9, 5, 4, 13, 9, 4, 5, 7, 6, 10, 6, 9, 6, 16, 6, 13, 6, 3, 6, 8, 7, 26, 11, 8, 4, 6, 7, 7, 6, 8, 7, 5, 24, 6, 8, 8, 8, 7, 8, 5, 6, 7, 9, 9, 6, 7, 4, 12, 6, 7, 8, 5, 6, 8, 5, 10, 6, 4, 21, 4, 3, 4, 8, 5, 11, 7, 11, 5, 9, 5, 8, 8, 5, 10, 5, 13, 10, 10, 10, 6, 7, 7, 6, 5, 9, 6, 10, 23, 7, 6, 8, 3, 12, 6, 15, 7, 10, 16, 9, 10, 7, 7, 4, 7, 4, 3, 4, 6, 5, 7, 10, 13, 6, 6, 6, 8, 8, 5, 12, 4, 6, 3, 4, 5, 6, 5, 7, 8, 7, 10, 3, 11, 10, 7, 4, 10, 21, 21, 7, 18, 12, 5, 6, 5, 7, 13, 9, 10, 6, 3, 3, 8, 18, 7, 4, 4, 6, 5, 4, 3, 12, 6, 8, 25, 11, 6, 8, 4, 5, 8, 5, 7, 10, 7, 4, 5, 6, 12, 6, 9, 6, 10, 4, 6, 3, 6, 6, 10, 7, 4, 3, 5, 3, 8, 9, 21, 7, 7, 15, 7, 22, 6, 7, 7, 7, 7, 5, 4, 5, 18, 9, 9, 9, 11, 5, 6, 4, 6, 4, 3, 4, 7, 7, 5, 10, 3, 4, 10, 2, 8, 5, 5, 6, 7, 6, 5, 12, 5, 9, 4, 12, 5, 7, 11, 9, 3, 16, 9, 5, 9, 8, 11, 9, 3, 5, 10, 9, 6, 6, 7, 8, 8, 9, 8, 14, 8, 11, 12, 5, 9, 7, 5, 9, 4, 8, 9, 2, 5, 8, 15, 5, 12, 4, 5, 6, 4, 6]
aOffset = [0, 2, 2, 8, 9, 14, 16, 20, 23, 25, 25, 29, 33, 36, 41, 46, 48, 53, 54, 59, 62, 65, 67, 69, 78, 81, 86, 95, 96, 101, 105, 109, 117, 123, 130, 138, 144, 154, 157, 162, 167, 172, 175, 179, 179, 183, 188, 191, 195, 201, 207, 207, 210, 213, 217, 218, 222, 228, 232, 239, 245, 257, 263, 272, 274, 280, 285, 287, 294, 299, 304, 310, 316, 321, 325, 328, 335, 339, 347, 349, 356, 358, 360, 369, 373, 379, 385, 393, 398, 398, 414, 421, 428, 429, 436, 440, 444, 448, 452, 455, 457, 459, 462, 462, 465, 468, 474, 478, 483, 487, 495, 498, 503, 508, 514, 518, 523, 527, 532, 539, 556, 563, 571, 577, 581, 589, 604, 619, 631, 643, 648, 662, 667, 674, 687, 694, 705, 708, 713, 717, 743, 755, 763, 770, 777, 779, 786, 793, 799, 805, 808, 820, 823, 838, 846, 850, 855, 877, 882, 886, 889, 895, 899, 916, 920, 928, 955, 962, 970, 976, 984, 992, 1000, 1008, 1019, 1025, 1032, 1037, 1046, 1054, 1064, 1070, 1077, 1090, 1096, 1121, 1133, 1142, 1152, 1157, 1161, 1169, 1177, 1182, 1192, 1199, 1206, 1209, 1219, 1229, 1241, 1258, 1262, 1266, 1272, 1279, 1287, 1291, 1294, 1299, 1309, 1313, 1321, 1333, 1342, 1345, 1356, 1365, 1372, 1375, 1382, 1389, 1396, 1401, 1408, 1413, 1417, 1424, 1438, 1443, 1451, 1461, 1465, 1473, 1483, 1486, 1495, 1499, 1508, 1512, 1520, 1528, 1536, 1547, 1551, 1558, 1562, 1570, 1592, 1602, 1605, 1615, 1619, 1628, 1644, 1650, 1659, 1667, 1683, 1686, 1696, 1701, 1715, 1720, 1727, 1734, 1741, 1750, 1770, 1779, 1787, 1791, 1797, 1805, 1811, 1816, 1826, 1829, 1840, 1843, 1855, 1860, 1864, 1868, 1879, 1889, 1894, 1898, 1903, 1910, 1917, 1937, 1951, 1963, 1970, 1973, 1978, 1983, 1993, 2003, 2015, 2020, 2027, 2034, 2041, 2052, 2057, 2066, 2080, 2083, 2092, 2100, 2105, 2112, 2122, 2127, 2135, 2139, 2148, 2160, 2167, 2176, 2181, 2186, 2191, 2215, 2222, 2228, 2238, 2246, 2258, 2265, 2270, 2278, 2287, 2297, 2306, 2312, 2323, 2329, 2337, 2344, 2348, 2360, 2367, 2374, 2378, 2384, 2390, 2401, 2416, 2428, 2432, 2436, 2442, 2449, 2463, 2473, 2479, 2483, 2490, 2501, 2508, 2515, 2521, 2531, 2537, 2548, 2552, 2557, 2567, 2574, 2579, 2581, 2587, 2595, 2602, 2610, 2624, 2641, 2655, 2668, 2679, 2696, 2706, 2715, 2722, 2725, 2729, 2737, 2744, 2752, 2758, 2767, 2770, 2775, 2783, 2793, 2802, 2812, 2821, 2836, 2843, 2850, 2854, 2863, 2868, 2872, 2885, 2894, 2898, 2903, 2910, 2916, 2926, 2932, 2941, 2947, 2963, 2969, 2982, 2988, 2991, 2997, 3005, 3012, 3038, 3049, 3057, 3061, 3067, 3074, 3081, 3087, 3095, 3102, 3107, 3131, 3137, 3145, 3153, 3161, 3168, 3176, 3181, 3187, 3194, 3203, 3212, 3218, 3225, 3229, 3241, 3247, 3254, 3262, 3267, 3273, 3281, 3286, 3296, 3302, 3306, 3327, 3331, 3334, 3338, 3346, 3351, 3362, 3369, 3380, 3385, 3394, 3399, 3407, 3415, 3420, 3430, 3435, 3448, 3458, 3468, 3478, 3484, 3491, 3498, 3504, 3509, 3518, 3524, 3534, 3557, 3564, 3570, 3578, 3581, 3593, 3599, 3614, 3621, 3631, 3647, 3656, 3666, 3673, 3680, 3684, 3691, 3695, 3698, 3702, 3708, 3713, 3720, 3730, 3743, 3749, 3755, 3761, 3769, 3777, 3782, 3794, 3798, 3804, 3807, 3811, 3816, 3822, 3827, 3834, 3842, 3849, 3859, 3862, 3873, 3883, 3890, 3894, 3904, 3925, 3946, 3953, 3971, 3983, 3988, 3994, 3999, 4006, 4019, 4028, 4038, 4044, 4047, 4050, 4058, 4076, 4083, 4087, 4091, 4097, 4102, 4106, 4109, 4121, 4127, 4135, 4160, 4171, 4177, 4185, 4189, 4194, 4202, 4207, 4214, 4224, 4231, 4235, 4240, 4246, 4258, 4264, 4273, 4279, 4289, 4293, 4299, 4302, 4308, 4314, 4324, 4331, 4335, 4338, 4343, 4346, 4354, 4363, 4384, 4391, 4398, 4413, 4420, 4442, 4448, 4455, 4462, 4469, 4476, 4481, 4485, 4490, 4508, 4517, 4526, 4535, 4546, 4551, 4557, 4561, 4567, 4571, 4574, 4578, 4585, 4592, 4597, 4607, 4610, 4614, 4624, 4626, 4634, 4639, 4644, 4650, 4657, 4663, 4668, 4680, 4685, 4694, 4698, 4710, 4715, 4722, 4733, 4742, 4745, 4761, 4770, 4775, 4784, 4792, 4803, 4812, 4815, 4820, 4830, 4839, 4845, 4851, 4858, 4866, 4874, 4883, 4891, 4905, 4913, 4924, 4936, 4941, 4950, 4957, 4962, 4971, 4975, 4983, 4992, 4994, 4999, 5007, 5022, 5027, 5039, 5043, 5048, 5054, 5058]
zText = "REINDEXEDESCAPEACHECKEYBEFOREIGNOREGEXPLAINSTEADDATABASELECTABLEFTHENDEFERRABLELSEXCEPTRANSACTIONATURALTERAISEXCLUSIVEXISTSCONSTRAINTERSECTRIGGEREFERENCESUNIQUERYATTACHAVINGROUPDATEMPORARYBEGINNERENAMEBETWEENOTNULLIKECASCADELETECASECOLLATECREATECURRENT_DATEDETACHIMMEDIATEJOINSERTMATCHPLANALYZEPRAGMABORTVALUESVIRTUALIMITWHENWHEREPLACEAFTERESTRICTANDEFAULTAUTOINCREMENTCASTCOLUMNCOMMITCONFLICTCROSSCURRENT_TIMESTAMPRIMARYDEFERREDISTINCTDROPFAILFROMFULLGLOBYIFINTOFFSETISNULLORDERIGHTOUTEROLLBACKROWUNIONUSINGVACUUMVIEWINITIALLYSLEEPSYSDATECONSTRAINT_SCHEMAEXECUTEARRAYLENSIMPLETEXTCOMPRESSROUTINE_CATALOGCONSTRAINT_NAMENOARCHIVELOGCURRENT_ROLEFORCEIMPLEMENTATIONQUOTANUMERICSPECIFIC_NAMEPERFORMTRANSLATIONMD5AUDITFULLPARAMATER_ORDINAL_POSITIONOCTET_LENGTHDISPATCHCURRENTVERSIONGOSEGMENTSIMILARROWNUMMINUTEMAPINSTANTIABLEMAXSUBCLASS_ORIGININSTANCEONLYCOBOLUSER_DEFINED_TYPE_NAMEASCIILOOPEXPNORMALHOLDCURRENT_TIMESTAMPUSERPREORDERDATETIME_INTERVAL_PRECISIONDEFINEDINTERVALROLLUPSNAPSHOTLOCATIONPOSITIONMODIFIESCONSTRAINTSUNNESTDEFINERCOUNTRECURSIVESEQUENCEASYMMETRICCALLEDLATERALDETERMINISTICEQUALSPARAMATER_SPECIFIC_SCHEMAGROUP_CONCATVALIDATORTRANSFORMSUNDERLASTVALIDATEIDENTITYNCHARCOMPLETIONBREADTHVERBOSEINTKEY_MEMBERORDINALITYTRIGGER_NAMETRANSATION_ACTIVEREALREADNOTICECOLLECTMAXTRANSNEXTREFFETCHNOMAXVALUELEFTNULLABLECATALOG_NAMESUBSTRINGDAYSCHEMA_NAMECOMMITTEDEXTRACTOUTCHARSETPACKAGETRACINGMOUNTPLACINGILIKEHOSTRECHECKPARAMETER_MODEUPPERDATAFILEDISCONNECTLIKEWHENEVEROVERRIDINGORDSTRUCTUREBODYEXCEPTIONCLOBDESCRIBEVARCHAR2SQLERRORCONSTRUCTORDATECHECKEDDATASMALLINTDATETIME_INTERVAL_CODEPARAMETERSAVGRESTRICTEDEXECCONCAT_WSCOLLATION_SCHEMABECOMELOAD_FILENATIONALCOMMAND_FUNCTIONABSNOMINVALUEFOUNDCOLLATION_NAMEREADSPROFILECOMPILERECOVERUNLIMITEDCHARACTER_SET_SCHEMAGENERATEDDISMOUNTCALLBITVARFREELISTBACKUPRESETASENSITIVEMINLANCOMPILERMIDCURRENT_DATEVALIDLINKFILECURSOR_NAMEINITIALIZEDEREFTRUESTYPEPREPARESERIAL8MESSAGE_OCTET_LENGTHLOCALTIMESTAMPSESSION_USERDECLARERAWEVERYNAMESCREATEUSERDICTIONARYSPECIFICTYPECROSSRETURNSSQLCODEITERATEINSENSITIVEFIRSTSYMMETRICMESSAGE_LENGTHDBAENCRYPTEDCONTAINSMONTHCLUSTERSAVE_POINTSCALETRUNCATESOMETRANSFORMCURRENT_USEROFFLINETRANSLATEFINALCHAINSHAREUSER_DEFINED_TYPE_SCHEMAPENDANTSTABLEDEALLOCATEBACKWARDCURRENT_PATHWITHOUTNCLOBNOTFOUNDTIMESTAMPSQLWARNINGTERMINATESIGNEDCHAR_LENGTHSTRICTCONTINUEPLPGSQLTIMECURRENT_TIMEUNKNOWNSECTIONCHARCANCELATOMICNORESETLOGSTIMEZONE_MINUTEMAXDATAFILESWORKRULESWITCHDISABLEROUTINE_SCHEMAARCHIVELOGNULLIFTRIMINITIALPCTINCREASEDECIMALINHERITFREEZENOCREATEDBCHANGEFIND_IN_SETROWSFALSEDESCRIPTORBOOLEANFLUSHDONOWAITENCODINGGRANTEDOPERATORTRIGGER_SCHEMARETURNED_SQLSTATEPARAMATER_NAMECORRESPONTINGDIAGNOSTICSCOLLATION_CATALOGBIT_LENGTHPARAMETEROPTIONSOFFBOTHRESOURCEPRIVATEALLOCATEONLINEAGGREGATEBITCLASSGROUPINGEXTERNALLYEXCLUDINGSUCCESSFULASSERTIONRETURNED_LENGTHNOAUDITFORWARDCOPYIMMUTABLERIGHTZONEMAXLOGHISTORYBENCHMARKROLEROWIDNOTHINGNOSORTPROCEDURALENGINEINDICATORENABLECONDITION_NUMBEROBJECTMAXLOGMEMBERSSUBSTRPADEXTENTABSOLUTECOMMENTPARAMETER_SPECIFIC_CATALOGSYSTEM_USERCOALESCELESSSQLBUFGENERALSESSIONMETHODOVERLAPSNATURALLEVELTRANSACTIONS_ROLLED_BACKMODULERELATIVESECURITYPARALLELPARTIALUNLISTENLISTSCURSORHANDLERINCLUDINGUPDATEXMLSHAREDRESTARTLOADCONCURRENTLYRETURNNOCACHECREATEDBSTDINMODIFYEXISTINGLARGETRANSATIONSTATICOIDSRETURNED_OCTET_LENGTHNONEGETWITHUNSIGNEDSYSIDREFERENCINGLOGFILECOLUMN_NAMETOASTPROCEDUREPRIOREXTERNALINITRANSINPUTMAXEXTENTSUNTILAUTHORIZATIONMINEXTENTSCHECKPOINTCONNECTIONNOTIFYSYNONYMROUTINEGLOBALSETOFSENSITIVEPASCALTABLESPACEPARAMETER_SPECIFIC_NAMEDESTROYREVOKEKEY_TYPEOLDMAXINSTANCESSOURCECHARACTERISTICSANALYSEIDENTIFIEDCHARACTER_LENGTHINCREMENTEXCEPTIONSUNNAMEDTRUSTEDSORTOVERLAYLOCKHEXFREESECONDMUMPSOPTIMALCONVERSIONTIMEZONE_HOURTHREADMANUALPREFIXVOLATILETEMPLATEOWNERCLASS_ORIGINTYPEPUBLICPLIMORELOWERSTDOUTCACHESTORAGEROWLABELFORTRANNAME_CONSTOWNSERVER_NAMEPRIVILEGESPCTUSEDMODESTATISTICSCHARACTER_SET_CATALOGCOMMAND_FUNCTION_CODELEADINGCONSTRAINT_CATALOGNOCREATEUSERALIASUNLOCKINNERVARCHARSTRAIGHT_JOINDELIMITERDESTRUCTORACCESSAREMODPRESERVEVERSION_COMPILE_OSPOSTFIXOVERMOVEBIGINTTREATTHANUIDEXTRACTVALUESEARCHSPECIFICUSER_DEFINED_TYPE_CATALOGUNENCRYPTEDEVENTSINHERITSGOTOGRANTDEFAULTSMERGEDATADIRREPEATABLEFOREACHYEARSCOPESERIALSERIALIZABLEBINARYRESETLOGSDOUBLEINDITCATORINT8LENGTHSQLOUTPUTDOMAINASSIGNMENTSUBLISTCUBEDECINOUTSCNLANGUAGESAVEPOINTDYNAMIC_FUNCTION_CODEDYNAMICCATALOGTRIGGER_CATALOGCONNECTTRANSACTIONS_COMMITTEDTABLESLOCATORVARYINGNOORDERINVOKERUSAGESIZESTARTCHARACTER_SET_NAMERETURNINGPRECISIONROW_COUNTCONTROLFILEINFIXLISTENRANDOPTIONDUMPSUMSTOPCONVERTINDEXESWHILETABLE_NAMENEWOPENNOCOMPRESSNOSQLSTATECLOSEARRAYSCHEMAPCTFREERESULTOUTERROUTINE_NAMEADMINISOLATIONSETSMESSAGE_TEXTWRITENOCYCLEMAXLOGFILESSTATEMENTADADYNAMIC_FUNCTIONTEMPORARYREUSEHIERARCHYMINVALUECARDINALITYFREELISTSUSEROLESDELIMITERSCHARACTERNUMBERSYSTEMTINYINTTRAILINGCONTENTSLOCALTIMETRIGGERSAUTO_INCREMENTMAXVALUEUNCOMMITTEDSQLEXCEPTIONBLOCKOPERATIONARCHIVECYCLEPARTITIONSHOWCASCADEDCOLLATIONATLOCALIMPLICITCONNECTION_NAMELAYERSTATEMENT_IDSELFSTATEMANAGELONGSCROLL"
aNext = [0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 38, 0, 32, 21, 0, 0, 0, 0, 29, 0, 0, 37, 0, 0, 0, 1, 55, 0, 0, 56, 0, 0, 0, 0, 0, 0, 0, 0, 0, 54, 0, 0, 0, 0, 30, 0, 16, 33, 10, 0, 0, 0, 0, 0, 0, 0, 11, 61, 68, 0, 8, 0, 93, 87, 0, 96, 0, 49, 0, 0, 64, 0, 41, 103, 0, 27, 107, 36, 62, 72, 0, 0, 57, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
weight = 50000

class SQLTokenizer():
    def __init__(self):
        self.words = []
        self.token_words = {}
        self.token_types = []
        self.keywords = []

    def sqlRunParser(self, zSql):
        i = 0
        while(i < len(zSql)):
            sLastTokenz = zSql[i:len(zSql)]
            sLastTokenn = 0
            sLastTokenn, tokenType = self.sqlGetToken(sLastTokenz, zSql, i)
            if sLastTokenn >= 1:
                # print zSql[i:i + sLastTokenn],tokenType
                self.words.append(zSql[i:i + sLastTokenn])
                self.token_types.append(tokenType)
                self.token_words[zSql[i:i + sLastTokenn]] = tokenType
            i = i + sLastTokenn

    def sqlGetToken(self, z, zSql, sLastTokenn):
        i = 0
        zv = z[0]

        if zv == ' ' or zv == '\t' or zv == '\n' or zv == '\f' or zv == '\r':
            i = 1
            for j in z:
                if(j.isspace()):
                    return i, TK_SPACE
        elif zv == '-':
            ta = 0
            if(1 < len(z)):
                ta = z[1]
            if 1 < len(z) and ta == '-':
                i = 2
                c = 0
                if(i < len(z)):
                    c = z[i]
                while(i < len(z) and c != '\n'):
                    c = z[i]
                    i = i + 1
                return i, TK_SPACE
            return 1, TK_MINUS
        elif zv == '(':
            return 1, TK_LP
        elif zv == ')':
            return 1, TK_RP
        elif zv == ';':
            return 1, TK_SEMI
        elif zv == '+':
            return 1, TK_PLUS
        elif zv == '*':
            return 1, TK_STAR
        elif zv == '/':
            ta = 0
            tb = 0
            if(1 < len(z)):
                ta = z[1]
            if(2 < len(z)):
                tb = z[2]

            if ta != '*' or ord(str(tb)) == 0:
                return 1, TK_SLASH
            i = 3
            c = 0
            if(2 < len(z)):
                c = z[2]
            while(i < len(z) and (c != '*' or z[i] != '/')):
                c = z[i]
                i = i + 1
                
            if c:
                i = i + 1
            return i, TK_SPACE

        elif zv == '%':
            return 1, TK_REM
        elif zv == '=':
            ta = 0
            if(1 < len(z)):
                ta = z[1]
            if ta == '=':
                return 2, TK_EQ
            return 1, TK_EQ
        elif zv == '<':
            c = 0
            if(1 < len(z)):
                c = z[1]
            if c == '=':
                return 2, TK_LE
            elif c == '>':
                return 2, TK_NE
            elif c == '<':
                return 2, TK_LSHIFT
            else:
                return 1, TK_LT
        elif zv == '>':
            c = 0
            if(1 < len(z)):
                c = z[1]
            if c == '=':
                return 2, TK_GE
            elif c == '>':
                return 2, TK_RSHIFT
            else:
                return 1, TK_GT
        elif zv == '!':
            ta = 0
            if(1 < len(z)):
                ta = z[1]
            if ta != '=':
                return 2, TK_ILLEGAL
            else:
                return 2, TK_NE
        elif zv == '|':
            ta = 0
            if(1 < len(z)):
                ta = z[1]
            if ta != '|':
                return 1, TK_BITOR
            else:
                return 2, TK_CONCAT
        elif zv == ',':
            return 1, TK_COMMA
        elif zv == '&':
            return 1, TK_BITAND
        elif zv == '~':
            return 1, TK_BITNOT
        elif zv == '"' or zv == '\'' or zv == '`':
            delim = z[0]
            y = sLastTokenn - 1
            i = 1
            c = 0
            if(i < len(z)):
                c = z[i]

            while(y >= 0):
                yc = zSql[y]
                if yc == delim:
                    break
                y = y - 1
            
            if y >= 0:
                while(i < len(z)):
                    c = z[i]
                    if c == delim:
                        if (i + 1 < len(z)) and (z[i + 1] == delim):
                            i = i + 1
                        else:
                            break
                    i = i + 1
                
                if(c == '\'' or c == '"'):
                    return i + 1, TK_STRING
                elif(i < len(z)):
                    return i + 1, TK_ID
                else:
                    return i, TK_ILLEGAL
            else:
                return 1, TK_START_TAG
        elif zv == '.':
            ta = 0
            if(1 < len(z)):
                ta = z[1]
            if str(ta).isdigit() is False:
                return 1, TK_DOT
        elif zv == '0' or zv == '1' or zv == '2' or zv == '3' or zv == '4' or zv == '5' or zv == '6' or zv == '7' or zv == '8' or zv == '9':
            i = 0
            tokenType = TK_INTEGER
            while(i < len(z) and z[i].isdigit()):
                i = i + 1
            if i < len(z) and z[i] == '.':
                i = i + 1
                while(i < len(z) and (z[i].isdigit())):
                    i = i + 1
                tokenType = TK_FLOAT
            if i < len(z):
                ta = 0
                tb = 0
                tc = 0
                if(i < len(z)):
                    ta = z[i]
                if(i + 1 < len(z)):
                    tb = z[i]
                if(i + 2 < len(z)):
                    tc = z[i]

                if ta == 'e' or ta == 'E' and tb.isdigit() or ((tb == '+' or tb == '-') and str(tc).isdigit()):
                    i += 2
                    while(i < len(z) and z[i].isdigit()):
                        i = i + 1
                    tokenType = TK_FLOAT
            while(i < len(z) and self.IdChar(z[i])):
                tokenType = TK_ILLEGAL
                i = i + 1
            return i, tokenType
        elif zv == '[':
            i = 1
            c = z[0]
            while(i < len(z) and c != ']'):
                c = z[i]
                i = i + 1
            if c == ']':
                return i, TK_ID
            else:
                return i, TK_ILLEGAL
        elif zv == '?':
            i = 1
            while(i < len(z) and z[i].isdigit()):
                i = i + 1
            return i, TK_VARIABLE
        elif zv == '#':
            i = 1
            while(i < len(z) and z[i].isdigit()):
                i = i + 1
            if i > 1:
                return i, TK_REGISTER
        elif zv == '@':
            pass 

        elif zv == ':':
            n = 0
            tokenType = TK_VARIABLE
            i = 1
            c = z[i]
            while(i < len(z)):
                c = z[i]
                if self.IdChar(c):
                    n = n + 1
                    
                elif c == '(' and n > 0:
                    i = i + 1
                    c = z[i]
                    while(i < len(z) and c.isspace() and c != ')'):
                        c = z[i]
                        i = i + 1
                    if c == ')':
                        i = i + 1
                    else:
                        tokenType = TK_ILLEGAL
                    break
                elif c == ':' and z[i + 1] == ':':
                    i = i + 1
                else:
                    break

                i = i + 1
                
            if n == 0:
                tokenType = TK_ILLEGAL
            return i, tokenType

        elif zv == 'x' or zv == 'X':
            ta = 0
            if(1 < len(z)):
                ta = z[1]
            if ta == '\'':
                tokenType = TK_BLOB
                i = 2
                c = 0
                if(i < len(z)):
                    c = z[i]
                while(i < len(z) and c != '\''):
                    c = z[i]
                    if c.isdigit() is False:
                        tokenType = TK_ILLEGAL
                    i = i + 1

                if i % 2 or c <= 0:
                    tokenType = TK_ILLEGAL
                if c:
                    i = i + 1
                return i, tokenType

        i = 1
        while(i < len(z) and self.IdChar(z[i])):
            i = i + 1
        tokenType = self.keywordCode(z, i)
        return i, tokenType
       

    def IdChar(self, c):
        vc = ord(c)
        sv = vc - 32

        if sv < 0: #\n 特殊处理   
            return False
        return (vc >= 66 or sqlIsEbcdicIdChar[sv] or vc == 45)

    def charMap(self, X):
        return ord(X.lower())

    def sqlStrNICmp(self, zLeft, zRight, N):
        a = zLeft
        b = zRight
        va = 0
        la = 0
        lb = 0
        if(len(a) > 0):
            va = ord(a[0])
        if(len(a) > 0):
            la = sqlUpperToLower[ord(a[0])]
        if(len(b) > 0):
            lb = sqlUpperToLower[ord(b[0])]

        while(N > 0 and va != 0 and la == lb):
            N = N - 1
            a = a[1:len(a)]
            b = b[1:len(b)]

            if(len(a) > 0):
                la = sqlUpperToLower[ord(a[0])]
            else:
                la = 0
            if(len(b) > 0):
                lb = sqlUpperToLower[ord(b[0])]
            else:
                lb = 0
            pass
        N = N - 1

        if(N < 0):
            return 0
        else:
            return la - lb


    def keywordCode(self, z, n):
        h = 0
        i = 0
        if n < 2: 
            return TK_ID
        h = ((self.charMap(z[0]) * 4) ^ (self.charMap(z[n - 1]) * 3) ^ n) % 127
        if isinstance(aHash[h], list):
            for m in aHash[h]:
                i =  m - 1
                while (i >= 0):
                    if(aLen[i] == n and self.sqlStrNICmp(zText[aOffset[i]:len(zText)],z,n) == 0):
                        self.keywords.append(z[:n])
                        return aCode[i] + weight
                    
                    i = (aNext[i]) - 1

        else:
            i = (aHash[h]) - 1
            while (i >= 0):
                if(aLen[i] == n and self.sqlStrNICmp(zText[aOffset[i]:len(zText)],z,n) == 0):
                    self.keywords.append(z[:n])
                    return aCode[i] + weight
                
                i = (aNext[i]) - 1
        return TK_ID
    
    def get_symbols(self):
        symbols = []
        specialSymbols = ["*","'",";","-","--","+","//","/","%","#","(",")"]
        for word in self.token_words.keys():
            if word in specialSymbols:
                symbols.append(word)

        return symbols
    


line = "' union select 0,username+CHR(124)+password,2,3,4,5,6,7,8,9 from admin union select * from news where 1=2 and ''='"
parser = SQLTokenizer()
parser.sqlRunParser(line)
print parser.token_words


