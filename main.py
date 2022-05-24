import random
import threading
import time
from PySide2.QtCore import QStringListModel
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide2.QtUiTools import QUiLoader
import pygame
import os
import cloudmusic
import requests as rq


class Gui:
    def __init__(self):
        self.ui = QUiLoader().load('UI.ui')
        self.ui.setWindowIcon(QIcon('music.ico'))
        self.ui.ButtonOpen.clicked.connect(self.opendir)
        self.ui.ButtonOpenfile.clicked.connect(self.openfile)
        self.ui.ButtonDownLoad.clicked.connect(self.download)
        self.ui.ButtonStop.clicked.connect(self.clickplay)
        self.ui.ButtonLast.clicked.connect(self.Bprev)
        self.ui.ButtonNext.clicked.connect(self.Bnext)
        self.ui.outList.clicked.connect(self.click)
        self.ui.printList.clicked.connect(self.clickdownload)
        self.ui.ButtonRandom.clicked.connect(self.BRand)
        self.file = ''
        self.dir = ''
        self.res = []
        self.ret = []
        self.num = 0
        self.pause = False
        self.unpause = False
        self.next = False
        self.prev = False
        self.ispause = False
        self.Rand = False
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'}
        self.cloud = 'https://music.163.com/song/media/outer/url?id='
        pygame.mixer.init()

    # 下载音乐
    def download(self):
        name = self.ui.idSearch.text()
        self.playlist = cloudmusic.search(name)
        musiclist = []
        for music in self.playlist:
            musiclist.append(music.name + ' ' + music.artist[0] + '.mp3')
        list_model = QStringListModel()
        list_model.setStringList(musiclist)
        self.ui.printList.setModel(list_model)

    def clickdownload(self, index):
        num = index.row()
        music = self.playlist[num]
        try:
            url = self.cloud + music.id + '.mp3'
            tmp = rq.get(url, headers=self.headers)
            tmp.raise_for_status()
            self.ui.stateEdit.setText('Successful')
            with open(f'cloudmusic/{music.artist[0]}-{music.name}.mp3', 'wb') as f:
                f.write(tmp.content)
        except:
            self.ui.stateEdit.setText('Failure')

    # 打开文件夹
    def opendir(self):
        try:
            self.dir = QFileDialog.getExistingDirectory(QMainWindow(), '选择文件夹')
            musics = [self.dir + '\\' + music for music in os.listdir(self.dir) if
                      music.endswith(('.mp3', '.flac', '.m4a'))]
            self.music(musics)
        except:
            pass

    # 打开文件
    def openfile(self):
        try:
            musics = QFileDialog.getOpenFileNames(QMainWindow(), '选择文件')[0]
            self.music(musics)
        except:
            pass

    # 加载音乐
    def music(self, musics):
        for i in musics:
            self.ret.append(os.path.basename(i))
            self.res.append(i.replace('\\', '/'))
        list_model = QStringListModel()
        list_model.setStringList(self.ret)
        self.ui.outList.setModel(list_model)

    # 单击选择音乐
    def click(self, index):
        self.num = index.row()
        pygame.mixer.init()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.thread_it()

    # 播放音乐
    def play(self):
        if len(self.res):
            while True:
                time.sleep(1)
                if self.pause:
                    try:
                        pygame.mixer.music.pause()
                        self.ui.ButtonStop.setText('继续')
                        self.pause = False
                        self.ispause = True
                    except:
                        pass

                elif self.unpause:
                    try:
                        pygame.mixer.music.unpause()
                        self.ui.ButtonStop.setText('暂停')
                        self.unpause = False
                        self.ispause = False
                    except:
                        pass
                elif self.next:
                    try:
                        pygame.mixer.music.stop()
                        if self.Rand:
                            self.rand()
                        else:
                            self.num += 1
                            if self.num == len(self.res):
                                self.num = 0
                        music = self.res[self.num]
                        pygame.mixer.music.load(music.encode())
                        pygame.mixer.music.play(1)
                        self.Now()
                        self.next = False
                    except:
                        pass
                elif self.prev:
                    try:
                        pygame.mixer.music.stop()
                        if self.Rand:
                            self.rand()
                        else:
                            if self.num == 0:
                                self.num = len(self.res) - 1
                            else:
                                self.num -= 1
                        music = self.res[self.num]
                        pygame.mixer.music.load(music.encode())
                        pygame.mixer.music.play(1)
                        self.Now()
                        self.prev = False
                    except:
                        pass
                elif not pygame.mixer.music.get_busy() and not self.ispause:
                    music = self.res[self.num]
                    pygame.mixer.music.load(music.encode())
                    pygame.mixer.music.play(1)
                    self.Now()
                    self.ui.ButtonStop.setText('暂停')
                    if self.Rand:
                        self.rand()
                    else:
                        if len(self.res) - 1 == self.num:
                            self.num = 0
                        else:
                            self.num = self.num + 1

    # 暂停继续
    def clickplay(self):
        if self.ui.ButtonStop.text() == '暂停':
            self.pause = True
        elif self.ui.ButtonStop.text() == '继续':
            self.unpause = True

    # 上一首
    def Bprev(self):
        self.prev = True

    # 下一首
    def Bnext(self):
        self.next = True

    # 随机播放
    def BRand(self):
        if self.ui.ButtonRandom.text() == '随机播放':
            self.Rand = True
            self.ui.ButtonRandom.setText('顺序播放')
        elif self.ui.ButtonRandom.text() == '顺序播放':
            self.Rand = False
            self.ui.ButtonRandom.setText('随机播放')

    # 随机选择
    def rand(self):
        self.num = random.randint(0, len(self.res) - 1)

    # 显示当前播放
    def Now(self):
        self.ui.nowList.setText(self.ret[self.num])

    # 开线程播放
    def thread_it(self):
        t = threading.Thread(target=self.play)
        t.setDaemon(True)
        t.start()


app = QApplication([])
gui = Gui()
gui.ui.show()
app.exec_()
