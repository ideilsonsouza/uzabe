from lib.uzabe.system import ZDCSystem
import time
import machine


class ZDCBoot:
    MAX_TENTATIVES = 10
    SLEEP_DURATION = 20  # em segundos

    def __init__(self):
        self.tentative = 0
        self.system_device = ZDCSystem()

    def initialization(self):
        _initialization = self.system_device.start_system_device()

        while not _initialization and self.tentative < self.MAX_TENTATIVES:
            print("Sistema não inicializado")
            self.tentative += 1
            try:
                time.sleep(self.SLEEP_DURATION)
                _initialization = self.system_device.start_system_device()
            except Exception as e:
                print(f"Erro: {e}")
                if self.tentative >= self.MAX_TENTATIVES:
                    self.restart_system()

        if not _initialization:
            print("Máximo de tentativas atingido. Reiniciando...")
            self.restart_system()

    def restart_system(self):
        print(f"Sistema vai ser reiniciado em {self.SLEEP_DURATION}s")
        time.sleep(self.SLEEP_DURATION)
        machine.reset()


if __name__ == "__main__":
    boot_process = ZDCBoot()
    boot_process.initialization()
