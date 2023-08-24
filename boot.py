from zdc_system import ZDCSystem
import time
import machine


class ZDCBoot:
    tentative = 0

    @staticmethod
    def initialization():
        system_device = ZDCSystem()
        _initialization = system_device.start_system_device()
        while not _initialization:
            try:
                print(f"Sistema não inicializado")
                ZDCBoot.tentative += 1
                time.sleep(20)
                _initialization = system_device.start_system_device()
            except Exception as e:
                print(f"Erro: {e}")
                if ZDCBoot.tentative >= 3:
                    print(f"Sistema vai ser reiniciado em 20s")
                    time.sleep(20)
                    machine.reset()

ZDCBoot.initialization()
